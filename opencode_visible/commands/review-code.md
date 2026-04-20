---
description: Revisión de código exhaustiva: convenciones, seguridad, performance, aislamiento multi-tenant.
agent: orchestrator
---

Voy a hacer una revisión de código completa. Coordina los revisores en paralelo:

1. **`@code-reviewer`** — pasa principal: convenciones del proyecto (snake_case BD, mapeo TypeORM, read-before-write), manejo de errores, tests.
2. **`@security-engineer`** — revisa si el cambio toca auth, RLS, inputs públicos, secretos, subida de archivos, o cualquier superficie de ataque.
3. **`@performance-engineer`** — si el cambio toca queries de BD, bucles sobre colecciones potencialmente grandes, o reportes, que revise plan de ejecución y patrones N+1.
4. Si el cambio toca fiscal/contable: **`@colombian-compliance-expert`** valida que cumpla norma.

Consolida los hallazgos en un solo reporte con formato:

```
## Veredicto
✅ / 🟡 / 🔴

## Hallazgos bloqueantes
- [SEC] ...
- [CONV] ...

## Sugerencias
- [PERF] ...
- [COMP] ...

## Lo bien hecho
- ...

## Próximos pasos
- ...
```

**Código a revisar** (archivo, PR, diff, o módulo): $ARGUMENTS
