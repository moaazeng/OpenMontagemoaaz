"""Noor async SQLite WAL store.

Holds presets (.noorpreset round-trippable), projects (.noorproj),
export history, and mastery/XP (+150 XP per export). Single source of
truth for the Noor workstation's local vault.
"""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import aiosqlite

from .schemas import DSPConfig, Preset


@dataclass(frozen=True)
class Mastery:
    """User mastery record for a domain (e.g. 'audio_master')."""

    domain: str
    xp: int
    exports_count: int
    last_export_at: Optional[float] = None


class NoorStore:
    """Async SQLite WAL store for Noor presets, projects, and mastery."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self.db_path = str(db_path)
        self._lock = asyncio.Lock()
        self._db: Optional[aiosqlite.Connection] = None

    # ── lifecycle ───────────────────────────────────────────────────────────

    async def init(self) -> None:
        """Open the DB (WAL) and create tables; seed official presets."""
        self._db = await aiosqlite.connect(self.db_path)
        await self._db.execute("PRAGMA journal_mode=WAL")
        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS presets (
                name TEXT PRIMARY KEY,
                dsp_config TEXT NOT NULL,
                lut_style TEXT NOT NULL,
                aspect_ratio TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """
        )
        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                name TEXT PRIMARY KEY,
                version TEXT NOT NULL,
                payload TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
            """
        )
        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS mastery (
                domain TEXT PRIMARY KEY,
                xp INTEGER NOT NULL DEFAULT 0,
                exports_count INTEGER NOT NULL DEFAULT 0,
                last_export_at REAL
            )
            """
        )
        await self._db.commit()
        await self._seed_presets()

    async def close(self) -> None:
        if self._db is not None:
            await self._db.close()
            self._db = None

    async def _seed_presets(self) -> None:
        """Seed the 8 official studio presets if absent."""
        official = [
            ("kadyrov_master", {"preamp_gain": 2.0, "lut_intensity": 90}, "kadyrov_gold", "9:16"),
            ("capcut_pro_elite", {"preamp_gain": 1.5, "eq_band_1_gain_db": 4.0}, "royal_dark", "9:16"),
            ("kadyrov_elite_bass", {"deep_bass_mix": 0.9, "preamp_gain": 1.2}, "makkah_sunrise", "9:16"),
            ("podcast_serat_sawy", {"preamp_gain": 1.4, "eq_band_2_gain_db": -2.0}, "pure_mushaf", "16:9"),
            ("viral_islam_sobhi", {"lut_intensity": 85, "preamp_gain": 1.6}, "dawn_spiritual", "9:16"),
            ("viral_hazza_albalushi", {"preamp_gain": 1.3, "eq_band_3_gain_db": 3.0}, "amber_glow", "9:16"),
            ("grand_mosque_haram", {"preamp_gain": 1.8, "lut_intensity": 100}, "makkah_sunrise", "9:16"),
            ("pro_studio_master", {"preamp_gain": 1.0, "lut_intensity": 50}, "pure_mushaf", "16:9"),
        ]
        import time

        now = time.time()
        for name, dsp, lut, ar in official:
            existing = await self._db.execute(
                "SELECT 1 FROM presets WHERE name = ?", (name,)
            )
            if await existing.fetchone() is None:
                await self._db.execute(
                    "INSERT INTO presets (name, dsp_config, lut_style, aspect_ratio, created_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (name, json.dumps(dsp), lut, ar, now),
                )
        await self._db.commit()

    # ── preset CRUD ─────────────────────────────────────────────────────────

    async def save_preset(self, preset: Preset) -> None:
        """Upsert a preset into the store."""
        assert self._db is not None
        import time

        await self._db.execute(
            "INSERT INTO presets (name, dsp_config, lut_style, aspect_ratio, created_at) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(name) DO UPDATE SET "
            "dsp_config=excluded.dsp_config, "
            "lut_style=excluded.lut_style, "
            "aspect_ratio=excluded.aspect_ratio, "
            "created_at=excluded.created_at",
            (
                preset.name,
                json.dumps(preset.dsp_config),
                preset.lut_style,
                preset.aspect_ratio,
                time.time(),
            ),
        )
        await self._db.commit()

    async def get_preset(self, name: str) -> Optional[Preset]:
        """Return a preset by name, or None."""
        assert self._db is not None
        cur = await self._db.execute(
            "SELECT name, dsp_config, lut_style, aspect_ratio FROM presets WHERE name = ?",
            (name,),
        )
        row = await cur.fetchone()
        if row is None:
            return None
        return Preset(
            name=row[0],
            dsp_config=json.loads(row[1]),
            lut_style=row[2],
            aspect_ratio=row[3],
        )

    async def list_presets(self) -> list[dict[str, str]]:
        """List all presets as dict rows (name, lut_style, aspect_ratio)."""
        assert self._db is not None
        cur = await self._db.execute(
            "SELECT name, lut_style, aspect_ratio FROM presets ORDER BY name"
        )
        return [
            {"name": r[0], "lut_style": r[1], "aspect_ratio": r[2]}
            for r in await cur.fetchall()
        ]

    async def export_preset(self, name: str) -> Optional[str]:
        """Export a preset to a JSON string (a .noorpreset payload)."""
        preset = await self.get_preset(name)
        if preset is None:
            return None
        return preset.model_dump_json()

    async def import_preset(self, payload: str) -> Optional[Preset]:
        """Import a preset from a .noorpreset JSON payload and persist it."""
        data = json.loads(payload)
        preset = Preset.model_validate(data)
        await self.save_preset(preset)
        return preset

    # ── project CRUD ────────────────────────────────────────────────────────

    async def save_project(self, project: Any) -> None:
        """Upsert a NoorProject (or any object with .model_dump_json())."""
        assert self._db is not None
        import time

        payload = project.model_dump_json() if hasattr(project, "model_dump_json") else json.dumps(project)
        name = project.name if hasattr(project, "name") else str(project)
        version = getattr(project, "version", "1.0")
        await self._db.execute(
            "INSERT INTO projects (name, version, payload, updated_at) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(name) DO UPDATE SET "
            "version=excluded.version, payload=excluded.payload, updated_at=excluded.updated_at",
            (name, version, payload, time.time()),
        )
        await self._db.commit()

    async def load_project(self, name: str) -> Optional[dict[str, Any]]:
        """Return a project payload dict by name, or None."""
        assert self._db is not None
        cur = await self._db.execute(
            "SELECT version, payload FROM projects WHERE name = ?", (name,)
        )
        row = await cur.fetchone()
        if row is None:
            return None
        return {"name": name, "version": row[0], "payload": json.loads(row[1])}

    # ── mastery / XP ────────────────────────────────────────────────────────

    async def record_export(self, domain: str, duration_seconds: float) -> Mastery:
        """Record an export: +150 XP per export, update count and timestamp."""
        assert self._db is not None
        import time

        now = time.time()
        cur = await self._db.execute(
            "SELECT xp, exports_count, last_export_at FROM mastery WHERE domain = ?",
            (domain,),
        )
        row = await cur.fetchone()
        if row is None:
            await self._db.execute(
                "INSERT INTO mastery (domain, xp, exports_count, last_export_at) "
                "VALUES (?, 150, 1, ?)",
                (domain, now),
            )
            xp, count = 150, 1
        else:
            xp, count = row[0] + 150, row[1] + 1
            await self._db.execute(
                "UPDATE mastery SET xp = ?, exports_count = ?, last_export_at = ? "
                "WHERE domain = ?",
                (xp, count, now, domain),
            )
        await self._db.commit()
        return Mastery(domain=domain, xp=xp, exports_count=count, last_export_at=now)

    async def get_mastery(self, domain: str) -> Mastery:
        """Return the mastery record for a domain (zeros if none)."""
        assert self._db is not None
        cur = await self._db.execute(
            "SELECT xp, exports_count, last_export_at FROM mastery WHERE domain = ?",
            (domain,),
        )
        row = await cur.fetchone()
        if row is None:
            return Mastery(domain=domain, xp=0, exports_count=0)
        return Mastery(domain=domain, xp=row[0], exports_count=row[1], last_export_at=row[2])
