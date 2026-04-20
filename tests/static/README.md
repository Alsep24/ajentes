# Static runtime checks

## 1) Safety lint (blocking)

```bash
python scripts/lint_runtime_safety.py
```

Enforces local-safe constraints on active prompt files:
- no hardcoded `PGPASSWORD='real_value'`
- no absolute local paths (`/home/...`, `~/AxiomaERP/...`)
- no `*.backup` files under `opencode_visible/agents`

## 2) Compatibility lint (advisory)

```bash
python scripts/lint_runtime_compat_advisory.py
```

Advisory-only checks:
- `default_agent` resolvable by canonical name or allowed legacy alias
- command `agent:` resolvable by canonical name or allowed legacy alias
- files in `instructions` exist
- exactly one `mode: primary`

## 3) Memory lint (advisory)

```bash
python scripts/lint_runtime_memory_advisory.py
```

Advisory-only checks:
- detects prompts/commands that mention `claude-mem`, `Neo4j`, `Nodos Maestros`, `search`, `get_observations`
- warns when memory-critical prompts do not include explicit fallback/degraded behavior
- warns when phrases like `prioridad absoluta` appear without explicit local-critical limits

## Blocking vs advisory
- Blocking: `lint_runtime_safety.py`
- Advisory: `lint_runtime_compat_advisory.py`, `lint_runtime_memory_advisory.py`

Advisory checks remain non-blocking until external runtime contracts are confirmed.
