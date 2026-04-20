# Gobernanza Multiagente (canónica + transición)

## 1) Nombres canónicos de agentes
Fuente de verdad: archivos `opencode_visible/agents/*.md`.

Canónicos actuales:
`arch`, `ba`, `db`, `db-migrations`, `db-performance`, `devops`, `dian`, `docs`, `godev`, `godev-integrations`, `godev-reports`, `mig`, `nestdev`, `orq`, `perf`, `pm`, `qa`, `qa-fiscal`, `qa-integration`, `qa-unit`, `release`, `review`, `sec`, `sec-data`, `support`, `ux`, `vuedev`, `vuedev-forms`, `vuedev-reports`.

## 2) Aliases legacy soportados temporalmente (advisory)
| Legacy | Canónico |
|---|---|
| orchestrator | orq |
| product-manager | pm |
| business-analyst | ba |
| software-architect | arch |
| database-architect | db |
| colombian-compliance-expert | dian |
| go-backend-engineer | godev |
| nestjs-backend-engineer | nestdev |
| vue-frontend-engineer | vuedev |
| ui-ux-designer | ux |
| security-engineer | sec |
| qa-engineer | qa |
| performance-engineer | perf |
| code-reviewer | review |
| release-manager | release |
| devops-engineer | devops |
| documentation-writer | docs |
| support-engineer | support |
| data-migration-specialist | mig |

## 3) Regla para introducir nuevos aliases
Se requiere:
1. Justificación de compatibilidad.
2. Mapeo explícito legacy -> canónico en esta guía.
3. Fecha objetivo de deprecación.
4. Validación en lint advisory.

## 4) Política de deprecación
Estados:
- `active`: permitido en transición.
- `deprecated`: se admite con warning advisory.
- `sunset-ready`: candidato a bloqueo en validación.

## 5) Criterio para pasar de advisory a blocking
Un chequeo de compatibilidad pasa a blocking solo cuando:
1. Contrato de runtime externo está confirmado.
2. Alias legacy fue comunicado y migrado en comandos/prompts.
3. Existe rollback documentado.

## 6) Validaciones recomendadas
- Seguridad local (blocking): `scripts/lint_runtime_safety.py`
- Compatibilidad (advisory): `scripts/lint_runtime_compat_advisory.py`


## 7) Gobernanza de memoria (M1 local)

Cuando un prompt/comando dependa de `claude-mem`, `Neo4j`, `Nodos Maestros`, `search` o `get_observations`:

1. Debe declarar cláusula explícita de fallback/degradación.
2. Debe explicitar el estado de memoria usado (`fresh`, `stale`, `unavailable`) cuando aplique.
3. Debe evitar decisiones implícitas no trazables si la memoria está `unavailable`.

### Regla de autoridad con límites
La frase “prioridad absoluta” de Nodos Maestros se interpreta como prioridad de dominio, pero **no** anula:
- políticas locales críticas de seguridad,
- hard constraints de runtime local documentadas,
- controles de gobernanza obligatorios del repositorio.

### Criterio de calidad para prompts críticos
Prompts críticos (orquestador, comandos, arquitectura, DB/QA/seguridad con dependencia de memoria) deben incluir:
- condición de fallback,
- comportamiento en modo degradado,
- reconciliación posterior cuando memoria vuelva a estar disponible.
