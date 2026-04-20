---
description: Triaging de incidente en producción: recolecta evidencia, identifica causa probable, escala al especialista correcto.
agent: orchestrator
---

Hay un incidente. Actúa rápido pero con disciplina:

1. **`@support-engineer`** arranca el triaging:
   - Transcribe literal el reporte del cliente.
   - Confirma alcance (cuántas empresas/usuarios).
   - Clasifica severidad P0/P1/P2/P3.
   - Intenta reproducir en staging.
   - Recolecta evidencia (logs, timestamps, payloads, queries lentas).
2. **Consulta `claude-mem`** — ¿hemos tenido este síntoma antes? Si sí, recupera la solución previa.
3. Según la evidencia, escala:
   - Bug de cálculo fiscal → **`@colombian-compliance-expert`** + **`@go-backend-engineer`** (o `@nestjs-backend-engineer`).
   - Lentitud / timeout → **`@performance-engineer`** + **`@database-architect`**.
   - Error 500 / panic → backend engineer directo.
   - Datos cross-tenant visibles → **INCIDENTE P0**: **`@security-engineer`** toma liderazgo, backend engineer apoya, **`@release-manager`** prepara comunicación.
   - Pérdida de datos → P0: **`@database-architect`** y **`@devops-engineer`** activan plan de restauración.
4. **`@release-manager`** coordina hotfix si aplica (versión patch, plan abreviado, rollback listo).
5. **`@qa-engineer`** agrega test de regresión **antes** del deploy del fix (inviolable).
6. Tras mitigación, **post-mortem sin culpas** en 48h (documento `incidents/YYYY-MM-DD-<slug>.md`).

Durante P0/P1, entrega actualizaciones cada 30 min aunque no haya avance — el cliente necesita saber que estás en el caso.

**Reporte del incidente**: $ARGUMENTS
