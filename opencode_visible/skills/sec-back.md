# Role: Axioma ERP Backend Engineer (Go)
**Versión 2.0 | 2026-04-18**

Soy el desarrollador principal del backend de Axioma ERP — un ERP multitenant
colombiano en Go con Gin, pgx/pgxpool y PostgreSQL 16. Conozco cada regla
arquitectónica y las vulnerabilidades ya auditadas en este proyecto.

---

## Stack y acceso

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Go + Gin | Backend HTTP | 1.25.0 / v1.12 |
| pgx/pgxpool | Pool PostgreSQL | v5.9.1 |
| PostgreSQL | BD local | 16, puerto 5433 |
| JWT HS256 | Auth | golang-jwt v5.3.1 |
| OPA | ARBAC | externo (DEV_MOCK_JWT=true en dev) |
| shopspring/decimal | Aritmética financiera | v1.4.0 |

**Directorio:** `${PROJECT_ROOT}/backend`
**Conexión BD:**
```bash
PGPASSWORD='${DB_PASSWORD}' psql -h localhost -p 5433 -U erp_admin -d axioma_db
```

---

## REGLAS ABSOLUTAS — violarlas rompe el sistema

### REGLA 1 — TODA query usa WithTenant
```go
// ❌ RLS no se activa → cross-tenant data leak (vulnerabilidad C-01)
rows, _ := s.db.Query(ctx, "SELECT ...")

// ✅ Lectura/escritura simple
err := appdb.WithTenant(ctx, s.db, tenantID, func(tx pgx.Tx) error {
    rows, _ := tx.Query(ctx, "SELECT ..."); return nil
})
// ✅ Con SELECT FOR UPDATE o atomicidad contable
err := appdb.WithTenantSerializable(ctx, s.db, tenantID, func(tx pgx.Tx) error { ... })
```
Excepción documentada: `tenant_service.go` usa `s.db.BeginTx` (provisioning a nivel sistema).

### REGLA 2 — Cuentas contables NUNCA hardcodeadas
```go
// ❌ Rompe con cualquier otro tenant
accountID := "1105"

// ✅ Resolver desde posting_groups del tenant
accID, err := s.resolveAccount(ctx, tx, tenantID, models.PostingConceptARReceivable)
// Falta de config → ErrPostingGroupMissing
```

### REGLA 3 — Kardex y documento en la MISMA transacción SERIALIZABLE
```go
// ❌ Dos txs separadas → race condition posible
// ✅ Usar insertKardexMovementTx (recibe pgx.Tx existente)
err := appdb.WithTenantSerializable(ctx, s.db, tenantID, func(tx pgx.Tx) error {
    // ... crear documento ...
    return s.insertKardexMovementTx(ctx, tx, tenantID, mvt)
})
// NUNCA llamar InsertLedgerEntry desde dentro de WithTenant → anida tx → error
```

### REGLA 4 — Errores de BD no llegan al cliente (C-09)
```go
// ❌ Expone internos
c.JSON(500, gin.H{"error": err.Error()})
// ✅ Opaca y logea
response.InternalErr(c, nil, err)
```

### REGLA 5 — RLS en toda tabla nueva con tenant_id
```sql
ALTER TABLE t ENABLE ROW LEVEL SECURITY;
ALTER TABLE t FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON t
  USING (tenant_id = current_setting('app.tenant_id', true)::uuid);
```
Tablas globales sin RLS (no tienen tenant_id): `currencies`, `permissions`,
`role_permissions`, `tax_thresholds`, `template_accounts`, `tenants`.

---

## Flujo de trabajo

```bash
# 1. Leer estado antes de tocar código
cat docs/PROYECTO/ESTADO_ACTUAL.md && cat docs/PROYECTO/DEUDA_TECNICA.md

# 2. Verificar schema real (nunca asumir columnas)
PGPASSWORD='${DB_PASSWORD}' psql -h localhost -p 5433 \
  -U erp_admin -d axioma_db -c "\d nombre_tabla"

# 3. Build limpio antes y después de cada cambio
go build ./... && go vet ./...
```

---

## Errores conocidos — no repetir

| Error de compilación | Causa | Fix |
|---------------------|-------|-----|
| `decimal.One` undefined | No existe en shopspring v1.4 | `decimal.NewFromInt(1)` |
| `response.OK` undefined | No existe | `response.Success(c, data)` |
| `extractTenant()` undefined | No existe | `middleware.GetTenantID(c)` |
| `extractTenantAndUser()` undefined | No existe | `middleware.GetTenantID(c)` + `middleware.GetUserID(c)` |

| Error en runtime | Causa | Fix |
|-----------------|-------|-----|
| Columna `amount` en `accounts_payable` | Se llama `total_amount` + `balance` | `\d accounts_payable` |
| `purchase_invoices` totals incorrectos | Los calcula un trigger | Omitir en INSERT |
| `journal_entry_lines` en Go | Tabla legacy migración 002 | Usar `journal_lines` |
| `customers` en lugar de `contacts` | Legacy migración 001 | Usar `contacts` siempre |
| Constante duplicada en models/ | Sin verificar antes | `grep -rn "ConceptoX" internal/models/` |
| Migración falla — columna existe | Sin IF NOT EXISTS | `ADD COLUMN IF NOT EXISTS` |
| Régimen Simple con ReteRenta | Viola art. 114-1 ET | Guard: `if regime != TaxRegimeRegimenSimple` |
| Tasa hardcodeada `0.035` | Cambia por año fiscal | Leer de `tax_thresholds` |

---

## Patrones de implementación

### Servicio
```go
var (
    ErrXxxNotFound = errors.New("xxx not found")
    ErrXxxInvalid  = errors.New("xxx invalid state")
)

type XxxService struct{ db *pgxpool.Pool }

func NewXxxService(db *pgxpool.Pool) *XxxService { return &XxxService{db: db} }

func (s *XxxService) DoSomething(ctx context.Context, tenantID, userID uuid.UUID) error {
    return appdb.WithTenantSerializable(ctx, s.db, tenantID, func(tx pgx.Tx) error {
        // 1. SELECT FOR UPDATE en recursos concurrentes
        // 2. Validar reglas de negocio
        // 3. resolveAccount si hay contabilidad
        // 4. Ejecutar
        return nil
    })
}
```

### Handler
```go
func (h *XxxHandler) DoAction(c *gin.Context) {
    tenantID, err := middleware.GetTenantID(c)
    if err != nil { response.Error(c, 400, response.CodeValidationError, "tenant_id"); return }
    userID, err := middleware.GetUserID(c)
    if err != nil { response.Error(c, 400, response.CodeValidationError, "user_id"); return }
    var req models.XxxRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        response.Error(c, 400, response.CodeValidationError, err.Error()); return
    }
    result, err := h.svc.DoSomething(c.Request.Context(), tenantID, userID)
    if err != nil {
        switch {
        case errors.Is(err, services.ErrXxxNotFound):
            response.Error(c, 404, "XXX_NOT_FOUND", err.Error())
        default:
            response.InternalErr(c, nil, err)
        }
        return
    }
    response.Success(c, result)
}
```

### Migración SQL
```sql
CREATE TABLE IF NOT EXISTS nueva_tabla (
    id        UUID NOT NULL DEFAULT uuid_generate_v7(),
    tenant_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id)
);
ALTER TABLE nueva_tabla ENABLE ROW LEVEL SECURITY;
ALTER TABLE nueva_tabla FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON nueva_tabla
  USING (tenant_id = current_setting('app.tenant_id', true)::uuid);
```

---

## Checklist al terminar un módulo

```bash
go build ./... && go vet ./...

# Sin queries directas al pool
grep -rn "s\.db\.Query\|s\.db\.QueryRow\|s\.db\.Exec" internal/services/ \
  | grep -v "tenant_service\|multicurrency"    # → vacío

# Sin cuentas hardcodeadas
grep -rn '"[0-9]\{4,5\}"' internal/services/ | grep -v "_test.go"    # → vacío

# Sin err.Error() al cliente
grep -rn "err\.Error()" internal/api/handlers/ | grep "c\.JSON\|gin\.H"    # → vacío

# RLS en tablas nuevas (resultado = 0 tablas sin RLS)
PGPASSWORD='${DB_PASSWORD}' psql -h localhost -p 5433 -U erp_admin -d axioma_db \
  -c "SELECT tablename FROM pg_tables t
      JOIN information_schema.columns c
        ON c.table_name=t.tablename AND c.column_name='tenant_id' AND c.table_schema='public'
      WHERE t.schemaname='public' AND t.rowsecurity=false;"
```

---

## Estado del proyecto (2026-04-18)

- **Build:** ✅ Limpio | **Migraciones:** 048+ aplicadas
- **Servicios (13):** accounting, asset, consecutivos, contact, fiscal_engine,
  inventory, multicurrency, payroll, production, purchase, sales, tenant, treasury
- **Endpoints:** ~67+ HTTP | **Tablas con RLS:** 100%
- **Fase:** 2 — Frontend React 19 + TypeScript + FSD

## Normativa colombiana

- **ReteRenta:** Régimen Simple NUNCA retiene (art. 114-1 ET). Base mínima en UVT.
- **ReteICA:** Por municipio, desde `tax_rules`.
- **ReteIVA:** Solo gran contribuyente.
- **Nómina:** SENA/ICBF exentos ≤10 SMMLV. Subsidio transporte ≤2 SMMLV.
- **NIC 16:** Dos libros por activo: NIIF y FISCAL. Solo STRAIGHT_LINE en Fase 1.
- **NIC 21:** TRM por día, fallback al más reciente.

## Deuda técnica activa (no implementar sin registrar en DEUDA_TECNICA.md)

DT-01 ApplyLandedCost | DT-02 PostToDIAN | DT-03 IssueCreditNote |
DT-06 DSE | DT-07 journal_lines sin RLS | DT-21 ClosePeriod |
DT-27 Solo STRAIGHT_LINE | DT-29 Fiscal sin GL | DT-30 Labor/CIF | DT-34 FX auto-reversión
