---
description: Prepara y ejecuta un release del ERP con plan completo (CI, migraciones, smoke tests, rollback).
agent: orchestrator
---

Voy a coordinar un release. Delega en orden:

1. **Consulta `claude-mem`** para verificar si hay releases previos recientes con incidentes — no repitas errores.
2. **`@release-manager`**:
   - Decide versión SemVer (major/minor/patch) según cambios.
   - Genera CHANGELOG.md con los commits desde el último tag.
   - Redacta notas de versión técnicas y notas para usuario final.
3. **`@devops-engineer`**:
   - Valida Dockerfiles y docker-compose.yml.
   - Confirma que el pipeline CI esté verde.
   - Prepara backup pre-deploy.
   - Construye y publica imágenes con tag de versión.
4. **`@database-architect`** revisa migraciones pendientes:
   - ¿Son retrocompatibles?
   - ¿Se pueden aplicar en caliente o requieren ventana?
   - ¿Existe plan de rollback de BD?
5. **`@qa-engineer`** define smoke tests post-deploy (lista concreta, ejecutable en <5 min).
6. **`@security-engineer`** confirma que no hay vulnerabilidades críticas en dependencias (`govulncheck` / `npm audit`) y que rotaciones de secretos, si aplican, estén programadas.
7. **`@release-manager`** consolida todo en `releases/vX.Y.Z/PLAN.md` con:
   - Ventana
   - Pasos detallados
   - Smoke tests
   - Plan de rollback
   - Stakeholders a notificar

Entrega al usuario:
- El `PLAN.md`.
- Un checklist ejecutable (markdown con casillas).
- El comando exacto para iniciar el deploy.

**Versión / scope del release**: $ARGUMENTS
