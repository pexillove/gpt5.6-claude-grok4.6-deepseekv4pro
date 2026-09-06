#!/usr/bin/env python3
"""Six-seat CHA pack injector. Original packs live under desktop/src/lib/packs."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

APP_TITLE = "gpt6 Astra-claude-grok4.6-deepseekv4pro-glm5.3-gemini破甲越狱"
ACTIVATION_WORD = "冷咖啡"
CONTROL_WORD = "BREAK//OPEN"
PACK_IDS = ("codex", "claude", "grok", "deepseek", "glm53", "gemini")
SEAT_ALIASES = {
    "codex": "codex",
    "gpt-6-astra": "codex",
    "gpt6-astra": "codex",
    "claude": "claude",
    "grok": "grok",
    "grok-4.6": "grok",
    "deepseek": "deepseek",
    "deepseek-v4-pro": "deepseek",
    "glm53": "glm53",
    "glm-5.3": "glm53",
    "gemini": "gemini",
}


def resolve_seat(name: str) -> str:
    key = name.strip().lower().replace(" ", "-")
    if key not in SEAT_ALIASES:
        raise ValueError(f"unknown seat: {name}")
    return SEAT_ALIASES[key]


def packs_dir() -> Path:
    here = Path(__file__).resolve().parent
    candidate = here / "desktop" / "src" / "lib" / "packs"
    if candidate.is_dir():
        return candidate
    raise FileNotFoundError("packs directory missing")


def markers(seat_id: str) -> tuple[str, str]:
    tag = seat_id.upper()
    return f"<!-- CHA-{tag}-POJIA:BEGIN -->", f"<!-- CHA-{tag}-POJIA:END -->"


def wrap_marked(seat_id: str, body: str) -> str:
    begin, end = markers(seat_id)
    text = body.rstrip() + "\n"
    if begin in text and end in text:
        return text
    return f"{begin}\n{text}{end}\n"


def render_pack(seat_id: str) -> str:
    raw = (packs_dir() / f"{seat_id}.md").read_text(encoding="utf-8")
    text = (
        raw.replace("{{APP_TITLE}}", APP_TITLE)
        .replace("{{ACTIVATION_WORD}}", ACTIVATION_WORD)
        .replace("{{CONTROL_WORD}}", CONTROL_WORD)
        .replace("{{SEAT_ID}}", seat_id)
    )
    return wrap_marked(seat_id, text)


def _home_of(env_keys: tuple[str, ...], folder: str) -> Path:
    for key in env_keys:
        value = os.environ.get(key)
        if value:
            return Path(value).expanduser().resolve()
    return Path.home() / folder


def seat_home(seat_id: str, override: str | os.PathLike[str] | None = None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    mapping = {
        "codex": _home_of(("CODEX_HOME", "CODEX_DIR"), ".codex"),
        "claude": _home_of(("CLAUDE_CONFIG_DIR", "CLAUDE_HOME"), ".claude"),
        "grok": _home_of(("GROK_HOME", "GROK_DIR"), ".grok"),
        "deepseek": _home_of(("DEEPSEEK_HOME", "DEEPSEEK_DIR"), ".deepseek"),
        "glm53": _home_of(("GLM_HOME", "ZCODE_HOME", "ZHIPU_HOME"), ".glm"),
        "gemini": _home_of(("GEMINI_HOME", "GEMINI_DIR"), ".gemini"),
    }
    return mapping[seat_id]


def extra_homes(override: str | os.PathLike[str] | None = None) -> dict[str, Path]:
    if override:
        root = Path(override).expanduser().resolve()
        return {"hermes": root / "hermes", "zcode": root / "zcode"}
    return {
        "hermes": _home_of(("HERMES_HOME",), ".hermes"),
        "zcode": _home_of(("ZCODE_HOME",), ".zcode"),
    }


def _split(text: str, begin: str, end: str) -> tuple[str, str, str]:
    start = text.index(begin)
    stop = text.index(end) + len(end)
    return text[:start], text[start:stop], text[stop:]


def insert_marked(previous: str, pack: str, begin: str, end: str) -> str:
    body = pack if pack.endswith("\n") else pack + "\n"
    if begin in previous and end in previous:
        head, _mid, tail = _split(previous, begin, end)
        return (head + body + tail).rstrip() + "\n"
    if previous.strip():
        return previous.rstrip() + "\n\n" + body
    return body


def wipe_marked(text: str, begin: str, end: str) -> str:
    if begin not in text or end not in text:
        return text
    head, _mid, tail = _split(text, begin, end)
    return (head + tail).strip()


def _snapshot_once(src: Path, dest: Path) -> bool:
    if dest.exists() or not src.exists():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(src.read_bytes())
    return True


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8", newline="\n")


def upsert_toml_string(src: str, key: str, value: str) -> str:
    line = f'{key} = {json.dumps(value)}'
    pattern = re.compile(rf"^[ \t]*{re.escape(key)}[ \t]*=[ \t]*.*$", re.M)
    if pattern.search(src):
        return pattern.sub(line, src)
    trimmed = src if not src or src.endswith("\n") else src + "\n"
    return trimmed + f"\n# CHA managed\n{line}\n"


def patch_json_filename(path: Path, name: str) -> None:
    data: dict = {}
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data = loaded
        except json.JSONDecodeError:
            data = {}
    context = data.get("context")
    if not isinstance(context, dict):
        context = {}
    names = context.get("fileName") or context.get("filename") or []
    if isinstance(names, str):
        names = [names]
    if not isinstance(names, list):
        names = []
    if name not in names:
        names.append(name)
    context["fileName"] = names
    data["context"] = context
    _write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def posix_path(path: Path) -> str:
    return path.resolve().as_posix()


def plan(seat_id: str, override: str | os.PathLike[str] | None = None) -> dict:
    home = seat_home(seat_id, override)
    extra = extra_homes(override)
    begin, end = markers(seat_id)
    pack = render_pack(seat_id)
    if seat_id == "codex":
        instruct = home / "prompts" / "cha-codex.md"
        writes = [
            {"kind": "file", "file": instruct},
            {"kind": "marked", "file": home / "AGENTS.md"},
            {"kind": "toml", "file": home / "config.toml", "key": "model_instructions_file", "value": posix_path(instruct)},
        ]
    elif seat_id == "claude":
        writes = [
            {"kind": "marked", "file": home / "CLAUDE.md"},
            {"kind": "file", "file": home / "rules" / "cha-breakopen.md"},
        ]
    elif seat_id == "grok":
        writes = [
            {"kind": "marked", "file": home / "AGENTS.md"},
            {"kind": "file", "file": home / "rules" / "cha-breakopen.md"},
            {"kind": "file", "file": home / "skills" / "cha-breakopen" / "SKILL.md"},
        ]
    elif seat_id == "deepseek":
        hermes = extra["hermes"]
        writes = [
            {"kind": "marked", "file": home / "DEEPSEEK.md"},
            {"kind": "marked", "file": hermes / "SOUL.md", "home": hermes},
            {"kind": "file", "file": hermes / "skills" / "cha-deepseek" / "SKILL.md", "home": hermes},
        ]
    elif seat_id == "glm53":
        zcode = extra["zcode"]
        writes = [
            {"kind": "marked", "file": home / "GLM.md"},
            {"kind": "marked", "file": zcode / "AGENTS.md", "home": zcode},
        ]
    else:
        writes = [
            {"kind": "marked", "file": home / "GEMINI.md"},
            {"kind": "settings", "file": home / "settings.json", "name": "GEMINI.md"},
        ]
    return {"home": home, "writes": writes, "begin": begin, "end": end, "pack": pack}


def backup_dir(home: Path) -> Path:
    path = home / "cha-backups"
    path.mkdir(parents=True, exist_ok=True)
    return path


def preview(seat_id: str, home: str | os.PathLike[str] | None = None) -> dict:
    spec = plan(seat_id, home)
    return {
        "ok": True,
        "action": "preview",
        "seat": seat_id,
        "title": APP_TITLE,
        "home": str(spec["home"]),
        "write": [str(item["file"]) for item in spec["writes"]],
        "text": spec["pack"],
    }


def deploy(seat_id: str, home: str | os.PathLike[str] | None = None) -> dict:
    spec = plan(seat_id, home)
    snapped: list[str] = []
    written: list[str] = []
    begin, end, pack = spec["begin"], spec["end"], spec["pack"]
    for item in spec["writes"]:
        target: Path = item["file"]
        nest = item.get("home") or spec["home"]
        bak = backup_dir(nest) / f"{target.name}.bak"
        if _snapshot_once(target, bak):
            snapped.append(str(bak))
        if item["kind"] in {"file", "marked"}:
            previous = target.read_text(encoding="utf-8") if item["kind"] == "marked" and target.exists() else ""
            next_text = insert_marked(previous, pack, begin, end) if item["kind"] == "marked" else pack
            _write(target, next_text)
            written.append(str(target))
        elif item["kind"] == "toml":
            previous = target.read_text(encoding="utf-8") if target.exists() else ""
            _write(target, upsert_toml_string(previous, item["key"], item["value"]))
            written.append(str(target))
        elif item["kind"] == "settings":
            patch_json_filename(target, item["name"])
            written.append(str(target))
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    state = {
        "seat": seat_id,
        "title": APP_TITLE,
        "deployedAt": stamp,
        "home": str(spec["home"]),
        "writes": written,
        "backups": snapped,
        "marker": True,
        "ok": True,
        "action": "deploy",
    }
    _write(backup_dir(spec["home"]) / "state.json", json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    return state


def verify(seat_id: str, home: str | os.PathLike[str] | None = None) -> dict:
    spec = plan(seat_id, home)
    checks = []
    for item in spec["writes"]:
        target: Path = item["file"]
        exists = target.exists()
        text = target.read_text(encoding="utf-8") if exists else ""
        marker = True
        if item["kind"] in {"marked", "file"}:
            marker = spec["begin"] in text and spec["end"] in text
        elif item["kind"] == "toml":
            marker = "model_instructions_file" in text
        elif item["kind"] == "settings":
            marker = exists
        checks.append({"file": str(target), "exists": exists, "marker": marker, "bytes": len(text.encode("utf-8"))})
    ok = all(item["exists"] and item["marker"] for item in checks)
    return {
        "ok": ok,
        "action": "verify",
        "seat": seat_id,
        "home": str(spec["home"]),
        "checks": checks,
        "marker": ok,
    }


def restore(seat_id: str, home: str | os.PathLike[str] | None = None) -> dict:
    spec = plan(seat_id, home)
    restored: list[str] = []
    begin, end = spec["begin"], spec["end"]
    for item in spec["writes"]:
        target: Path = item["file"]
        nest = item.get("home") or spec["home"]
        bak = backup_dir(nest) / f"{target.name}.bak"
        if bak.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(bak.read_bytes())
            restored.append(str(target))
            continue
        if not target.exists():
            continue
        if item["kind"] in {"toml", "settings"}:
            continue
        text = target.read_text(encoding="utf-8")
        if item["kind"] == "file" and begin in text:
            target.unlink()
            restored.append(str(target))
            continue
        if item["kind"] == "marked":
            cleaned = wipe_marked(text, begin, end)
            if cleaned:
                _write(target, cleaned + "\n")
            else:
                target.unlink()
            restored.append(str(target))
    return {"ok": True, "action": "restore", "seat": seat_id, "restored": restored, "home": str(spec["home"])}


def run(seat_id: str, verb: str, home: str | os.PathLike[str] | None = None) -> dict:
    seat_id = resolve_seat(seat_id) if seat_id not in PACK_IDS else seat_id
    if verb in {"preview"}:
        return preview(seat_id, home)
    if verb in {"run", "deploy"}:
        return deploy(seat_id, home)
    if verb in {"check", "verify"}:
        return verify(seat_id, home)
    if verb == "restore":
        return restore(seat_id, home)
    raise ValueError(f"unknown seat verb: {verb}")


ACTIONS = {
    "preview": lambda home=None: preview("gemini", home),
    "deploy": lambda home=None: deploy("gemini", home),
    "verify": lambda home=None: verify("gemini", home),
    "restore": lambda home=None: restore("gemini", home),
}
