---
description: Implementa un módulo o historia ya planificada, coordinando backend, frontend, pruebas y revisión.
agent: orchestrator
---

Voy a implementar un módulo/historia ya planificada. Coordina la cadena estándar:

1. **Consulta `claude-mem`** para recuperar el plan (ADR, historias, reglas de negocio) y decisiones previas.
2. Identifica el proyecto objetivo:
   - Si es `axioma-erp-backend` → **`@go-backend-engineer`** implementa.
   - Si es EDI-ERP → **`@nestjs-backend-engineer`** implementa backend y **`@vue-frontend-engineer`** implementa UI.
3. Si requiere cambios de esquema: **`@database-architect`** entrega migración primero, backend la consume después.
4. Si toca reglas fiscales: **`@colombian-compliance-expert`** valida los valores antes de que el engineer hardcodee nada (mejor catálogo parametrizable).
5. Tras implementación, delega a **`@qa-engineer`** para pruebas unitarias, de integración y test de aislamiento multi-tenant.
6. Luego a **`@code-reviewer`** para revisión formal.
7. Si `@code-reviewer` devuelve bloqueantes → vuelve al engineer original.
8. Si todo pasa → a **`@documentation-writer`** para actualizar docs.
9. Cierra entregando resumen con archivos tocados, pruebas ejecutadas, y siguiente paso (release).

**Requisito inviolable**: cada implementador termina con su comando de verificación (`go build ./... && go vet ./... && go test ./... -count=1` o equivalente npm). Si falla, no declaramos terminado.

**Módulo/historia a implementar**: $ARGUMENTS
