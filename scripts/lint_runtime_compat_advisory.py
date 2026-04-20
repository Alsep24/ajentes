#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / "opencode_visible" / "agents"
COMMANDS_DIR = ROOT / "opencode_visible" / "commands"
CONFIG_PATH = ROOT / "opencode_visible" / "opencode.json"

LEGACY_TO_CANONICAL = {
    "orchestrator": "orq",
    "product-manager": "pm",
    "business-analyst": "ba",
    "software-architect": "arch",
    "database-architect": "db",
    "colombian-compliance-expert": "dian",
    "go-backend-engineer": "godev",
    "nestjs-backend-engineer": "nestdev",
    "vue-frontend-engineer": "vuedev",
    "ui-ux-designer": "ux",
    "security-engineer": "sec",
    "qa-engineer": "qa",
    "performance-engineer": "perf",
    "code-reviewer": "review",
    "release-manager": "release",
    "devops-engineer": "devops",
    "documentation-writer": "docs",
    "support-engineer": "support",
    "data-migration-specialist": "mig",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def resolve_agent(name: str, canonical: set[str]) -> tuple[bool, str]:
    if name in canonical:
        return True, name
    mapped = LEGACY_TO_CANONICAL.get(name)
    if mapped and mapped in canonical:
        return True, mapped
    return False, ""


def advisory() -> list[str]:
    warnings: list[str] = []
    canonical = {p.stem for p in AGENTS_DIR.glob("*.md")}

    # exactly one primary
    primary = []
    for p in sorted(AGENTS_DIR.glob("*.md")):
        t = read_text(p)
        m = re.match(r"^---\n(.*?)\n---", t, re.S)
        if m and re.search(r"^mode:\s*primary\s*$", m.group(1), re.M):
            primary.append(p.stem)
    if len(primary) != 1:
        warnings.append(f"[primary] expected 1 primary, found {len(primary)}: {primary}")

    if CONFIG_PATH.exists():
        cfg = json.loads(read_text(CONFIG_PATH))

        default_agent = cfg.get("default_agent")
        if isinstance(default_agent, str):
            ok, resolved = resolve_agent(default_agent, canonical)
            if not ok:
                warnings.append(f"[default_agent] unresolved '{default_agent}'")
            elif resolved != default_agent:
                warnings.append(
                    f"[default_agent] legacy '{default_agent}' resolves to canonical '{resolved}'"
                )

        instructions = cfg.get("instructions", [])
        if isinstance(instructions, list):
            for ins in instructions:
                if isinstance(ins, str) and not (ROOT / ins).exists():
                    warnings.append(f"[instructions] missing file '{ins}'")

    for cmd in sorted(COMMANDS_DIR.glob("*.md")):
        t = read_text(cmd)
        m = re.match(r"^---\n(.*?)\n---", t, re.S)
        if not m:
            warnings.append(f"[commands] missing frontmatter in {cmd.relative_to(ROOT)}")
            continue
        mm = re.search(r"^agent:\s*(\S+)\s*$", m.group(1), re.M)
        if not mm:
            warnings.append(f"[commands] missing agent field in {cmd.relative_to(ROOT)}")
            continue
        agent = mm.group(1)
        ok, resolved = resolve_agent(agent, canonical)
        if not ok:
            warnings.append(f"[commands] unresolved agent '{agent}' in {cmd.relative_to(ROOT)}")
        elif resolved != agent:
            warnings.append(
                f"[commands] legacy agent '{agent}' in {cmd.relative_to(ROOT)} resolves to '{resolved}'"
            )

    return warnings


def main() -> int:
    warnings = advisory()
    print("Runtime compatibility advisory checks:")
    if not warnings:
        print(" - none")
    else:
        for w in warnings:
            print(f" - {w}")
    # advisory only
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
