# Contrato Local de Memoria (M1)

## 1) Rol de `claude-mem` en la arquitectura
`claude-mem` actúa como capa externa de memoria semántica para recuperar y persistir decisiones/contexto histórico usados por orquestador, comandos y agentes especializados.

Este repositorio NO implementa integración runtime directa con `claude-mem`; define gobernanza local, validaciones y contrato esperado.

## 2) Relación entre componentes
- **Repo local**: políticas, prompts, comandos, gobernanza y linters.
- **Agentes/comandos**: consumen contexto de memoria para mejorar decisiones.
- **Skills**: referencia auxiliar, no autoridad primaria.
- **Memoria externa (`claude-mem`/Neo4j)**: estado de dominio y decisiones históricas.

## 3) Definición de Nodos Maestros
“Nodos Maestros” = registros de alto valor decisional en la memoria externa (por ejemplo ADRs, convenciones obligatorias, decisiones transversales).

En M1, su autoridad se modela por gobernanza documental, no por enforcement runtime.

## 4) Modelo de autoridad recomendado
1. **Políticas críticas locales del repo** (seguridad/hard constraints, no negociables)
2. **Memoria de dominio vigente** (Nodos Maestros)
3. **Prompts/procedimientos de agentes y comandos**
4. **Skills auxiliares**

Regla: “prioridad absoluta” de memoria NO anula políticas locales críticas.

## 5) Política de fallback/degradación
Cuando la memoria no está disponible, el sistema debe degradar de forma explícita y trazable.

Estados sugeridos:
- `fresh`: memoria consultada y válida para la decisión actual.
- `stale`: memoria disponible pero potencialmente desactualizada.
- `unavailable`: memoria no disponible (error/timeout/no acceso).

## 6) Decisión en modo degradado
En estado `unavailable`:
1. continuar con contexto local del repo,
2. declarar supuestos explícitos,
3. marcar la respuesta como modo degradado,
4. solicitar reconciliación posterior con memoria cuando sea posible.

## 7) Trazabilidad mínima esperada
Toda decisión sensible debería registrar:
- `memory_state` (`fresh|stale|unavailable`),
- referencia de nodos (si existen),
- si se usó fallback,
- supuestos aplicados en degradación,
- acción de reconciliación pendiente.

## 8) Alcance de M1
Este contrato es local y advisory.
No introduce llamadas reales a `claude-mem` ni modifica contratos externos del runtime.
