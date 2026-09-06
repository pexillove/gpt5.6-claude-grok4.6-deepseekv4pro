#!/usr/bin/env python3
"""Temp-home roundtrip for all six CHA seats."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from seats import PACK_IDS, activation_reply, deploy, preview, render_pack, restore, verify  # noqa: E402

STAMPS = {
    "codex": "ASTRA//UNLOCK",
    "claude": "ANTHRO//CLEAR",
    "grok": "GROK//OPEN",
    "deepseek": "SEEK//BARE",
    "glm53": "GLM//STRAIGHT",
    "gemini": "Gemini 席位上的冷咖啡执行核",
}


def main() -> int:
    bodies = {seat: render_pack(seat) for seat in PACK_IDS}
    if len(set(bodies.values())) != len(PACK_IDS):
        raise SystemExit("packs are not unique")
    for seat, stamp in STAMPS.items():
        if stamp not in bodies[seat]:
            raise SystemExit(f"{seat} missing original stamp")
    page = activation_reply()
    if "QQ一群 1057540028" not in page or "QQ二群 1077074552" not in page:
        raise SystemExit("activation page missing QQ groups")
    if "来杯冰美式，然后开始你的灰产人生吧。" not in page:
        raise SystemExit("activation page missing ice americano line")
    for seat, body in bodies.items():
        if "1057540028" not in body or "灰产人生" not in body:
            raise SystemExit(f"{seat} missing activation page")
    with tempfile.TemporaryDirectory(prefix="cha-seats-") as raw:
        root = Path(raw)
        for seat in PACK_IDS:
            home = root / seat
            pre = preview(seat, home)
            if not pre.get("ok"):
                raise SystemExit(f"{seat} preview failed")
            dep = deploy(seat, home)
            if not dep.get("ok"):
                raise SystemExit(f"{seat} deploy failed")
            ver = verify(seat, home)
            if not ver.get("ok"):
                raise SystemExit(f"{seat} verify failed: {ver}")
            res = restore(seat, home)
            if not res.get("ok"):
                raise SystemExit(f"{seat} restore failed")
    print("seat_selftest ok · " + ",".join(PACK_IDS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
