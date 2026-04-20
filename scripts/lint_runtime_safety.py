#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ACTIVE_DIRS = [
    ROOT / "opencode_visible" / "agents",
    ROOT / "opencode_visible" / "skills",
    ROOT / "opencode_visible" / "commands",
]

SECRET_PATTERNS = [
    re.compile(r"PGPASSWORD='(?!\$\{DB_PASSWORD\})[^']+'"),
]
ABS_PATH_PATTERNS = [
    re.compile(r"/home/[A-Za-z0-9._-]+/"),
    re.compile(r"~/AxiomaERP/"),
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def iter_active_markdown() -> list[Path]:
    files: list[Path] = []
    for d in ACTIVE_DIRS:
        if d.exists():
            files.extend(sorted(d.glob("*.md")))
    return files


def check_required() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for file in iter_active_markdown():
        text = read_text(file)
        rel = file.relative_to(ROOT)

        for pat in SECRET_PATTERNS:
            for m in pat.finditer(text):
                errors.append(f"[secret] {rel}: '{m.group(0)}'")

        for pat in ABS_PATH_PATTERNS:
            for m in pat.finditer(text):
                errors.append(f"[abs-path] {rel}: '{m.group(0)}'")

    backup_files = sorted((ROOT / "opencode_visible" / "agents").glob("*.backup"))
    for bf in backup_files:
        errors.append(f"[backup] {bf.relative_to(ROOT)}")

    # Advisory checks (local, comprobable) - do not fail build
    cfg_path = ROOT / "opencode_visible" / "opencode.json"
    if cfg_path.exists():
        cfg = json.loads(read_text(cfg_path))
        agent_names = {p.stem for p in (ROOT / "opencode_visible" / "agents").glob("*.md")}

        default_agent = cfg.get("default_agent")
        if isinstance(default_agent, str) and default_agent not in agent_names:
            warnings.append(
                f"[config-ref] default_agent '{default_agent}' not found in opencode_visible/agents/*.md"
            )

        instructions = cfg.get("instructions", [])
        if isinstance(instructions, list):
            for ins in instructions:
                if isinstance(ins, str) and not (ROOT / ins).exists():
                    warnings.append(f"[config-ref] instructions file missing: {ins}")

        for cmd in sorted((ROOT / "opencode_visible" / "commands").glob("*.md")):
            text = read_text(cmd)
            m = re.match(r"^---\n(.*?)\n---", text, re.S)
            if not m:
                continue
            mm = re.search(r"^agent:\s*(\S+)\s*$", m.group(1), re.M)
            if mm:
                command_agent = mm.group(1)
                if command_agent not in agent_names:
                    warnings.append(
                        f"[config-ref] {cmd.relative_to(ROOT)} uses agent '{command_agent}' not present as file stem"
                    )

    return errors, warnings


def main() -> int:
    errors, warnings = check_required()

    if errors:
        print("Required safety checks: FAIL")
        for err in errors:
            print(f" - {err}")
    else:
        print("Required safety checks: PASS")

    if warnings:
        print("Advisory compatibility warnings:")
        for w in warnings:
            print(f" - {w}")
    else:
        print("Advisory compatibility warnings: none")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
