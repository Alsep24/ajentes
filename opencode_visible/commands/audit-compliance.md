---
description: Auditoría de cumplimiento colombiano en un módulo (DIAN, PUC, NIIF, retenciones, habeas data).
agent: orchestrator
---

Voy a auditar el cumplimiento regulatorio colombiano del módulo indicado. Protocolo:

1. **`@colombian-compliance-expert`** genera checklist normativo aplicable al módulo:
   - Si es facturación: UBL 2.1, CUFE, resoluciones DIAN vigentes, notas crédito/débito con causales correctas, documento soporte.
   - Si es nómina: nómina electrónica (Res. 000013/2021+), PILA, prestaciones sociales, seguridad social.
   - Si es contabilidad: PUC, NIIF para Pymes, partida doble, cierres.
   - Si son retenciones: ET + DUR 1625/2016, bases en UVT vigentes, tarifas por concepto.
   - Si maneja datos personales: Ley 1581/2012 (habeas data), políticas, ARCO, retención.
2. **`@business-analyst`** y **`@code-reviewer`** verifican que el código/configuración del módulo cumpla cada ítem del checklist con evidencia (archivo:línea).
3. **`@qa-engineer`** propone pruebas automatizadas de cumplimiento (ej. "factura con base > 27 UVT aplica retención", "comprobante rechazado si no cuadra partida doble").
4. **`@security-engineer`** audita manejo de datos personales y auditoría de cambios.

Entrega informe `audits/<modulo>-YYYY-MM-DD.md`:

```
# Auditoría: <módulo>
**Fecha**: YYYY-MM-DD
**Marco aplicable**: DIAN Res. 000165/2023, ET art. X, NIIF Pymes sección Y, Ley 1581/2012

## Checklist
- [x] <ítem> — evidencia: `src/....go:LN`
- [ ] <ítem> — NO CUMPLE — brecha: <desc> — severidad: alto

## Hallazgos críticos
1. ...

## Recomendaciones
- <responsable> implementa <cambio> antes de <fecha>

## Próxima auditoría sugerida
<cuándo se revisa: típicamente cada ley anual / reforma tributaria>
```

**Módulo a auditar**: $ARGUMENTS
