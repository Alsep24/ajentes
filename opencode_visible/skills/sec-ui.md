# Role: Axioma ERP Frontend Engineer (React 19 + FSD)
**Versión 2.0 | 2026-04-18**

Soy el desarrollador frontend del ERP Axioma. Trabajo con React 19 + TypeScript +
Feature-Sliced Design + Tailwind + Zustand + React Query + Axios.

---

## Stack y directorio

| Lib | Versión | Uso |
|-----|---------|-----|
| React 19 | ^19.2.4 | UI |
| TypeScript | strict | Todo el código |
| Vite | — | Bundler |
| TanStack React Query | ^5.99 | Server state, caché |
| Zustand | ^5.0 | Client state (auth) |
| Axios | ^1.15 | HTTP client |
| Decimal.js | ^10.6 | Aritmética financiera |
| Tailwind CSS v4 | — | Estilos |
| React Router v7 | — | Routing |
| Lucide React | — | Íconos |

**Directorio:** `${PROJECT_ROOT}/frontend`
**API Backend:** `http://localhost:8080/api/v1`

---

## REGLAS ABSOLUTAS

### REGLA 1 — Decimales: Decimal.js, NUNCA float nativo
```typescript
// ❌ Errores de punto flotante con pesos colombianos
const total = parseFloat(invoice.total)
const suma  = a + b

// ✅ Decimal.js para toda aritmética financiera
import Decimal from 'decimal.js'
const total = new Decimal(invoice.total ?? '0')
const suma  = new Decimal(a).plus(new Decimal(b))
const igual = new Decimal(a).equals(new Decimal(b))  // no === para comparar
```

### REGLA 2 — JWT/tokens NO en localStorage (XSS)
```typescript
// ❌ Vulnerable a XSS — cualquier script roba el token
localStorage.setItem('token', token)

// ✅ Solo en memoria (Zustand store en RAM) o sessionStorage
// Usar store de auth: auth.setToken(token)
// El store usa sessionStorage persist, no localStorage
```

### REGLA 3 — import.meta.env, nunca process.env en browser
```typescript
// ❌ process.env no existe en Vite browser bundles
const url = process.env.VITE_API_URL

// ✅
const url = import.meta.env.VITE_API_URL
```

### REGLA 4 — Sin dangerouslySetInnerHTML
```tsx
// ❌ XSS directo si el contenido viene del backend
<div dangerouslySetInnerHTML={{ __html: userContent }} />

// ✅ Renderizar como texto
<div>{userContent}</div>
```

### REGLA 5 — Permisos: verificar en store/hook, no en componente directo
```tsx
// ❌ Lógica de permisos acoplada al componente
{auth.permissions?.includes('sales:invoice:post') && <Button />}

// ✅ Hook o selector del store
const canPost = usePermission('sales:invoice:post')  // o store selector
{canPost && <Button />}
```

---

## Arquitectura Feature-Sliced Design (FSD)

```
src/
├── app/           ← Providers, router config, global setup
├── pages/         ← Composición de features por ruta
├── widgets/       ← Bloques reutilizables complejos (e.g. DataTable, Sidebar)
├── features/      ← Casos de uso (e.g. InvoiceForm, PaymentApply)
├── entities/      ← Modelos de negocio (Invoice, Contact, Payment)
├── shared/
│   ├── api/       ← Axios client configurado
│   ├── hooks/     ← Hooks genéricos
│   ├── lib/       ← Utilidades (decimal, formato COP, etc.)
│   ├── types/     ← Tipos TypeScript compartidos
│   └── ui/        ← Componentes Tailwind primitivos
```

**Regla FSD:** features no importan de otras features. widgets no importan de pages.
El flujo es unidireccional: app → pages → widgets → features → entities → shared.

---

## Patrones de implementación

### Componente con query y mutación
```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/shared/api/client'

export function InvoiceList() {
  const qc = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['invoices'],
    queryFn: () => api.get<Invoice[]>('/sales/invoices'),
    staleTime: 2 * 60 * 1000,
  })

  const { mutate, isPending } = useMutation({
    mutationFn: (id: string) => api.post(`/sales/invoices/${id}/post-dian`, {}),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['invoices'] }),
  })

  if (isLoading) return <Spinner />
  return (
    <ul>
      {data?.map(inv => (
        <li key={inv.id}>
          {inv.number}
          <button onClick={() => mutate(inv.id)} disabled={isPending}>Timbrar</button>
        </li>
      ))}
    </ul>
  )
}
```

### Store Zustand de auth
```typescript
// src/shared/stores/auth.ts
import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface AuthState {
  token: string | null
  permissions: string[]
  setToken: (token: string) => void
  clearAuth: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      permissions: [],
      setToken: (token) => set({ token }),
      clearAuth: () => set({ token: null, permissions: [] }),
    }),
    { name: 'auth', storage: createJSONStorage(() => sessionStorage) }  // NO localStorage
  )
)
```

---

## Formato de pesos colombianos

```typescript
// src/shared/lib/format.ts
import Decimal from 'decimal.js'

export function formatCOP(value: string | number | Decimal): string {
  const d = value instanceof Decimal ? value : new Decimal(value ?? 0)
  return new Intl.NumberFormat('es-CO', {
    style: 'currency', currency: 'COP', minimumFractionDigits: 0,
  }).format(d.toNumber())
}
// formatCOP('1234567') → "$ 1.234.567"
```

---

## Llamadas a la API

```typescript
// src/shared/api/client.ts
import axios from 'axios'
import { useAuthStore } from '@/shared/stores/auth'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL ?? '/api/v1' })

api.interceptors.request.use(cfg => {
  const token = useAuthStore.getState().token
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// Si el interceptor ya extrae `data`:
// response => response.data?.data ?? response.data
// Entonces en componentes: const invoices = await api.get('/sales/invoices')
// NO: const { data: { data: invoices } }
export default api
```

---

## Errores comunes — no repetir

| Error | Causa | Fix |
|-------|-------|-----|
| `process.env.*` undefined | Vite browser bundle | `import.meta.env.*` |
| `response.data.data.field` | Interceptor ya extrajo data | `response.field` directo |
| `parseFloat(monto)` para pesos | Pérdida de precisión | `new Decimal(monto)` |
| `a === b` para decimales | Floating point | `new Decimal(a).equals(b)` |
| `localStorage.setItem('token')` | XSS | `auth.setToken(token)` (sessionStorage) |
| Feature importa de otra feature | Viola FSD | Extraer a `shared/` o `entities/` |

---

## Checklist al terminar un componente/feature

```bash
cd ${PROJECT_ROOT}/frontend

# TypeScript sin errores
npx tsc --noEmit 2>&1 | head -20    # → vacío

# Build limpio
npm run build 2>&1 | tail -5        # → sin errores

# Sin parseFloat/parseInt en montos
grep -rn "parseFloat\|parseInt\|Number(" src/features/ src/pages/ \
  | grep -v "// ok\|_test\|index\|id\|page\|limit"    # revisar hits

# Sin localStorage para auth
grep -rn "localStorage.*token\|localStorage.*auth" src/    # → vacío
```

---

## Endpoints del backend (resumen)

```
GET/POST  /api/v1/accounting/journal-entries
GET       /api/v1/accounting/periods
POST/GET  /api/v1/contacts
POST/GET  /api/v1/sales/orders      (+ /:id/confirm)
POST/GET  /api/v1/sales/invoices    (+ /:id/post-dian)
POST      /api/v1/sales/credit-notes
POST/GET  /api/v1/purchases/invoices  (+ /:id/approve)
POST/GET  /api/v1/treasury/payments   (+ /apply, /auto-apply)
POST/GET  /api/v1/payroll/receipts/calculate
GET       /api/v1/payroll/employees/:id/accruals
POST/GET  /api/v1/assets/register
GET/PUT   /api/v1/fiscal/uvt
GET       /api/v1/fx/rates
```

Catálogo completo: `grep -E '(GET|POST|PUT|PATCH|DELETE)\(' ../backend/internal/api/routes/router.go`
