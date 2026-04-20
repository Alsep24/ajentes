---
description: Planifica un feature nuevo del ERP coordinando PM, BA, arquitecto y compliance antes de implementar.
agent: orchestrator
---

Voy a planificar un nuevo feature del ERP. Coordina a los agentes necesarios siguiendo este protocolo:

1. **Consulta `claude-mem`** (`search` con palabras clave del feature) para ver si hay decisiones o trabajo previo relacionado.
   - Si `claude-mem` no está disponible, continúa en modo degradado con contexto local del repositorio, declara supuestos explícitos y deja reconciliación pendiente.
2. Delega a **`@product-manager`** para que escriba historias de usuario priorizadas con criterios de aceptación Gherkin.
3. Si el feature toca reglas fiscales/contables (retenciones, IVA, PUC, facturación, nómina, NIIF), delega en paralelo a **`@colombian-compliance-expert`** para validar el marco normativo vigente y a **`@business-analyst`** para detallar las reglas de negocio.
4. Delega a **`@software-architect`** para un ADR breve con las opciones de implementación, impacto multi-tenant y trade-offs.
5. Si hay impacto en esquema: suma a **`@database-architect`** para proponer migraciones y políticas RLS.
6. Si hay UI nueva: suma a **`@ui-ux-designer`** para wireframe y estados.
7. Consolida todo en un documento `features/<nombre>/PLAN.md` con:
   - Resumen ejecutivo (3-5 líneas).
   - Historias priorizadas.
   - Reglas de negocio y referencias normativas.
   - ADR de arquitectura.
   - Cambios de BD propuestos.
   - Wireframe (si aplica).
   - Estimación de esfuerzo (S/M/L/XL por historia).
   - Siguientes pasos (con quién implementa).

**Feature a planificar**: $ARGUMENTS
