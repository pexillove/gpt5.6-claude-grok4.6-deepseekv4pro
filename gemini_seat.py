#!/usr/bin/env python3
"""Gemini seat wrapper. Pack + inject live in seats.py."""

from __future__ import annotations

import os
from pathlib import Path

from seats import (
    ACTIONS,
    ACTIVATION_WORD,
    APP_TITLE,
    CONTROL_WORD,
    deploy as _deploy,
    markers,
    preview as _preview,
    render_pack,
    restore as _restore,
    seat_home,
    verify as _verify,
)

MARKER_BEGIN, MARKER_END = markers("gemini")


def pack_text() -> str:
    return render_pack("gemini")


def resolve_home(home: str | os.PathLike[str] | None = None) -> Path:
    return seat_home("gemini", home)


def preview(home: str | os.PathLike[str] | None = None) -> dict:
    return _preview("gemini", home)


def deploy(home: str | os.PathLike[str] | None = None) -> dict:
    return _deploy("gemini", home)


def verify(home: str | os.PathLike[str] | None = None) -> dict:
    return _verify("gemini", home)


def restore(home: str | os.PathLike[str] | None = None) -> dict:
    return _restore("gemini", home)
