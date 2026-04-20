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

This script is non-blocking by design until external runtime contracts are confirmed.
