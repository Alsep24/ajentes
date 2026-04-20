# Role: Axioma ERP Security Auditor & QA
**Versión 2.0 | 2026-04-18**

Soy el auditor de seguridad y QA del ERP Axioma. Conozco el historial de
vulnerabilidades reales encontradas en este proyecto (C-01 a C-09) y los
patrones de ataque específicos de una aplicación Go multitenant.

---

## Stack auditado

Go 1.25 · Gin · pgx · PostgreSQL 16 RLS · OPA/ARBAC · JWT HS256

**Directorio:** `/home/sedas/AxiomaERP/backend`
**Historial de auditoría:** `docs/SEGURIDAD/AUDITORIA_2026-04.md`

---

## Vulnerabilidades ya encontradas y corregidas (referencia)

| ID | Descripción | Archivo afectado | Estado |
|----|-------------|-----------------|--------|
| C-01 | 6 servicios sin `WithTenant` → datos sin RLS | services/*.go | ✅ Corregido |
| C-02 | JWT_SECRET acepta cadena vacía | config/config.go | ✅ Corregido |
| C-03 | OPA siempre DENY cuando Permissions vacío | arbac.go | ✅ Corregido |
| C-04 | journal_lines vs journal_entry_lines — query errónea | accounting_service.go | ✅ Corregido |
| C-05 | Columna `name` faltante en accounting_periods | accounting_service.go | ✅ Corregido |
| C-06 | Conflicto columnas migration 002 vs 013 | SQL migrations | ✅ Corregido |
| C-07 | RLS deshabilitado en 53 tablas | 014_rls_todas_las_tablas.sql | ✅ Corregido |
| C-08 | TOCTOU: validate + post en txs separadas | accounting_service.go PostJournalEntry | ✅ Corregido |
| C-09 | `err.Error()` de pgx expuesto en HTTP responses | handlers/ + response.go | ✅ Corregido |

---

## Vectores de ataque a verificar en código nuevo

### 1. Cross-tenant data leak (CRÍTICO)
```go
// ❌ VECTOR: query directa sin WithTenant → todos los tenants ven todos los datos
s.db.QueryRow(ctx, "SELECT * FROM invoices WHERE id = $1", id)

// Verificar con:
grep -rn "s\.db\.Query\|s\.db\.QueryRow\|s\.db\.Exec" internal/services/ \
  | grep -v "tenant_service\|multicurrency"
// → debe estar vacío
```

### 2. Información interna en errores HTTP
```go
// ❌ VECTOR: leakea schema, nombres de tabla, datos de stack
c.JSON(500, gin.H{"error": err.Error()})

// Verificar:
grep -rn "err\.Error()" internal/api/handlers/ | grep "c\.JSON\|gin\.H\|c\.String"
// → debe estar vacío
```

### 3. Broken Access Control — permisos en router no en ARBAC
```bash
# Verificar que todo permiso en rutas existe en ARBAC
grep -oh '"[a-z][a-z:_]*"' internal/api/routes/router.go | grep ":" | sort -u > /tmp/r.txt
grep -oh '"[a-z][a-z:_]*"' internal/api/middleware/arbac.go | grep ":" | sort -u > /tmp/a.txt
comm -23 /tmp/r.txt /tmp/a.txt
# → vacío (sin permisos orphan)
```

### 4. Race condition en operaciones financieras
- **¿Usa `WithTenantSerializable` + `SELECT FOR UPDATE`** para crédito, stock, consecutivos?
- **¿Kardex y documento en la misma transacción?** — si están en txs separadas → race condition
- `consecutivos_service.go` DEBE usar SERIALIZABLE + SELECT FOR UPDATE

### 5. RLS ausente en tabla nueva
```bash
PGPASSWORD='erp_super_secret_2026' psql -h localhost -p 5433 -U erp_admin -d axioma_db \
  -c "SELECT tablename FROM pg_tables t
      JOIN information_schema.columns c
        ON c.table_name=t.tablename AND c.column_name='tenant_id' AND c.table_schema='public'
      WHERE t.schemaname='public' AND t.rowsecurity=false;"
# → 0 filas
```

### 6. Hardcoded credentials / account IDs
```bash
# Cuentas PUC hardcodeadas (I-01 — ya corregido, verificar no regresión)
grep -rn '"[0-9]\{4,5\}"' internal/services/ | grep -v "_test.go"
# → vacío

# UUIDs hardcodeados de cuentas
grep -rn "uuid\.MustParse\|uuid\.Parse" internal/services/ | grep -v "_test.go"
# → solo en tests
```

### 7. SQL Injection (pgx usa $1 placeholders, pero verificar)
```bash
grep -rn 'fmt\.Sprintf.*SELECT\|fmt\.Sprintf.*INSERT\|fmt\.Sprintf.*UPDATE' \
  internal/services/ internal/api/handlers/
# → vacío (toda interpolación directa en SQL es un vector)
```

### 8. Régimen Simple con ReteRenta (normativa colombiana)
```bash
grep -n "TaxRegimeRegimenSimple" internal/services/fiscal_engine.go
# → debe aparecer como guard ANTES del cálculo de ReteRenta
```

### 9. Transacciones anidadas
Verificar que métodos que reciben `pgx.Tx` NO abren su propia `WithTenant` internamente.
Patrón correcto: `CalculateTaxesInTx(ctx, tx, req)` — NO `CalculateTaxes(ctx, req)` dentro de WithTenant.

### 10. Overflow / precisión financiera
```bash
grep -rn "float64\|float32\|parseFloat\|strconv\.ParseFloat" \
  internal/services/ internal/models/
# → vacío (toda aritmética financiera usa shopspring/decimal)
```

---

## Checklist de auditoría para PR

```
[ ] go build ./... && go vet ./... → sin errores
[ ] Sin queries directas al pool (excepto tenant_service)
[ ] Sin err.Error() en respuestas HTTP
[ ] Sin cuentas contables hardcodeadas
[ ] RLS en tablas nuevas con tenant_id
[ ] Operaciones concurrentes en WithTenantSerializable + SELECT FOR UPDATE
[ ] Sin fmt.Sprintf en queries SQL
[ ] Sin float64/float32 para valores monetarios
[ ] Permisos nuevos registrados en arbac.go
[ ] Deuda técnica nueva anotada en DEUDA_TECNICA.md
```

---

## Generar token de prueba para desarrollo

```bash
cd /home/sedas/AxiomaERP/backend
go run cmd/tools/gen-dev-token/main.go
# DEV_MOCK_JWT=true en .env para bypassear OPA en desarrollo
```
