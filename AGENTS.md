# AGENTS.md (root)

## Propósito del repositorio
Este repositorio define la configuración, orquestación y gobernanza de un sistema multiagente para flujos ERP especializados.

## Jerarquía de autoridad
1. **Configuración global** (`opencode_visible/opencode.json`)
2. **Orquestador primario** (`opencode_visible/agents/orq.md`)
3. **Comandos** (`opencode_visible/commands/*.md`)
4. **Subagentes** (`opencode_visible/agents/*.md`, excepto el primario)
5. **Skills auxiliares** (`opencode_visible/skills/*`, `agents_visible/skills/*`)

Si hay conflicto, prevalece el nivel superior en esta jerarquía.

## Política de naming canónico
- El nombre canónico de agente es el **stem del archivo** en `opencode_visible/agents/*.md`.
- Los comandos y referencias internas deben converger progresivamente a nombres canónicos.

## Política de aliases legacy
- Se permite compatibilidad temporal con aliases legacy documentados en `docs/GOVERNANCE_MULTIAGENTE.md`.
- Los aliases legacy son **advisory** hasta confirmar contrato del runtime externo.

## Política de deprecación
- Todo alias legacy debe tener:
  - equivalente canónico,
  - estado (`active`, `deprecated`),
  - criterio de retiro.
- Ningún alias se elimina sin ventana de transición documentada.

## Regla de no suposición de runtime
No se asume soporte de loaders, aliases o fallback no demostrados en este repositorio.
Toda compatibilidad no demostrada se trata como externa/no confirmada.

## Validaciones estáticas
- Seguridad local: `python scripts/lint_runtime_safety.py`
- Compatibilidad advisory: `python scripts/lint_runtime_compat_advisory.py`
