#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = [
    ROOT / "opencode_visible" / "agents",
    ROOT / "opencode_visible" / "commands",
    ROOT / "opencode_visible" / "skills",
]

MEMORY_PATTERNS = [
    re.compile(r"claude-mem", re.I),
    re.compile(r"Neo4j", re.I),
    re.compile(r"Nodos Maestros", re.I),
    re.compile(r"\bsearch\s*\(", re.I),
    re.compile(r"get_observations", re.I),
]

FALLBACK_PATTERNS = [
    re.compile(r"fallback", re.I),
    re.compile(r"degradad", re.I),
    re.compile(r"memory_unavailable", re.I),
    re.compile(r"si .*memoria.*no .*disponible", re.I),
    re.compile(r"unavailable", re.I),
]

CRITICAL_HINTS = [
    re.compile(r"mode:\s*primary", re.I),
    re.compile(r"agent:\s*orchestrator", re.I),
    re.compile(r"arquitect", re.I),
    re.compile(r"db|migrat|qa|security|sec-data", re.I),
]

EXTREME_AUTHORITY = re.compile(r"prioridad\s+absoluta", re.I)
LIMIT_AUTHORITY = re.compile(r"no\s+anula|pol[ií]ticas\s+locales\s+cr[ií]ticas|hard\s+constraints", re.I)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def is_critical(text: str, path: Path) -> bool:
    if path.parent.name == "commands":
        return True
    return any(p.search(text) for p in CRITICAL_HINTS)


def main() -> int:
    warnings: list[str] = []
    memory_mentions = 0

    for d in SCAN_DIRS:
        for file in sorted(d.glob("*.md")):
            text = read_text(file)
            rel = file.relative_to(ROOT)
            has_memory = any(p.search(text) for p in MEMORY_PATTERNS)

            if has_memory:
                memory_mentions += 1
                if is_critical(text, file) and not any(p.search(text) for p in FALLBACK_PATTERNS):
                    warnings.append(
                        f"[fallback-missing] {rel} depends on memory but no explicit fallback/degraded clause detected"
                    )

            if EXTREME_AUTHORITY.search(text) and not LIMIT_AUTHORITY.search(text):
                warnings.append(
                    f"[authority-limit-missing] {rel} uses 'prioridad absoluta' without explicit local-critical limit"
                )

    print("Runtime memory advisory checks:")
    print(f" - files with memory mentions: {memory_mentions}")
    if warnings:
        for w in warnings:
            print(f" - {w}")
    else:
        print(" - no advisory warnings")

    # advisory-only
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
