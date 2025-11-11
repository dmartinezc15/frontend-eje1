# The Football Shop — Frontend

**Tienda de fútbol** hecha con **React + Vite + TypeScript**.  
Sin backend: catálogo estático (`public/products.json`), carrito con **Zustand** (persistencia en `localStorage`), **drawer** lateral, **barra de checkout fija** y botón **“Pagar ahora”** vía *Payment Link* (o **WhatsApp** como fallback).

---

## ✨ Features
- Catálogo desde `public/products.json` (clubs, ligas, variantes, tallas, stock, etc.).
- Grilla responsive + **zoom** en imágenes.
- Búsqueda y **chips** de categorías.
- Carrito **persistente** (Zustand + localStorage) en **drawer** lateral.
- **Checkout bar** fija con total y **“Pagar ahora”** siempre visible.
- Tema visual “noche de estadio” ⚽.

---

## 🧰 Requisitos
- **Node.js 18+ / 20+** (frontend)
- **Python 3.11+** (backend)
- **npm** o **pnpm** (frontend), **pip** (backend)


---

## 🚀 Instalación y levantamiento

```bash
# 1) Clona el repo
git clone <TU_REPO>
cd frontend-eje1

# 2) Instala dependencias
npm i # o npm install

# 4) Dev server
npm run dev
# Abre la URL que muestra Vite (p.ej. http://localhost:5173)
```

---

## ⚙️ Configuración

### 1) Link de pago (opcional ya que es emulado)
Crea **.env** en la raíz con:
```env
# Link de pago simulado (reemplázalo por tu Payment Link real)
VITE_PAYMENT_LINK=https://example.com/checkout/football-shop?mode=test
```
> Si **no** defines `VITE_PAYMENT_LINK`, el botón **“Pagar ahora”** usará **WhatsApp** por defecto.

### 2) Número de WhatsApp
En `src/App.tsx`, reemplaza `57XXXXXXXXXX` por tu número en:
```ts
const waLink = `https://wa.me/57TU_NUMERO?text=${waText}`
```

### 3) Catálogo de productos
El archivo **`public/products.json`** define tu catálogo. Ejemplo robusto:
```json
[
  {
    "id": "kit-rm-home-26",
    "name": "Real Madrid Camiseta Home 25/26",
    "price": 599000,
    "img": "/img/real-madrid-home.webp",
    "category": "Ropa",
    "club": "Real Madrid",
    "league": "LaLiga",
    "season": "25/26",
    "variant": { "style": "Home", "color": "Blanco" },
    "sizes": ["S","M","L","XL"],
    "stock": 34,
    "tags": ["nuevo","top"],
    "rating": 4.8,
    "sku": "RM-HOME-26"
  }
]
```
> Las imágenes deben estar en `public/img/` y referenciarse con rutas absolutas (`/img/...`).

---

## 📂 Estructura
```
football-shop/
├─ public/
│  ├─ products.json           # catálogo estático
│  └─ img/                    # imágenes del catálogo
├─ src/
│  ├─ store/
│  │  └─ cart.ts              # store (Zustand + persist)
│  ├─ App.tsx                 # UI principal
│  ├─ App.css                 # estilos (tema fútbol + pro)
│  └─ main.tsx
├─ index.html
├─ package.json
├─ .env                       # VITE_PAYMENT_LINK (opcional)
└─ vite.config.ts
```

> Despliegue bajo subruta (p.ej. `/tienda/`): en `vite.config.ts` ajusta `base: '/tienda/'`.

---

## 🔧 Troubleshooting
- **No carga `products.json`** → verifícalo en `public/` y que la ruta sea `/products.json`.
- **Imágenes no visibles** → coloca archivos en `public/img/` y usa rutas `/img/...`.
- **Estado no persiste** → limpia `localStorage` o revisa permisos del navegador.

---

## 🗺️ Roadmap (Frontend)
- Selector de **tallas** y **variantes** en tarjeta y carrito.
- **Cupones** por % o valor fijo.
- **Compartir carrito** por URL.
- **PWA offline** con `vite-plugin_pwa`.
- Exportar pedido en **PDF/JSON**.

---

## 🌐 Arquitectura rápida
```
Frontend (Vite/React) ──▶ API FastAPI (JSON ahora, DB luego)
             ▲                 └─ /v1/products (GET, filtros)
             │                 └─ /v1/pricing/quote (POST, cupones/envío)
             └───────────────▶ └─ /v1/payment/link (GET)
```

---

## 🚀 Frontend — Instalación y levantamiento

```bash
# 1) Clona el repo
git clone <TU_REPO>
cd frontend-eje1

# 2) Instala dependencias
npm i  # o pnpm i

# 3) Variables opcionales
# .env
VITE_PAYMENT_LINK=https://example.com/checkout/football-shop?mode=test
VITE_API_URL=http://localhost:8000

# 4) Dev server
npm run dev  # o pnpm dev
# Abre http://localhost:5173
```

> Si **no** defines `VITE_API_URL`, puedes seguir usando `products.json`.  
> Si **sí** lo defines, el front consumirá la API (`/v1/products`).

---

## 🔌 Backend — FastAPI

### Estructura
```
api/
  app/
    main.py
    config.py
    models.py
    repository.py
    services.py
  data/
    products.json      # catálogo robusto (ids, sizes, variant, stock, etc.)
  requirements.txt
  Dockerfile
```

### requirements.txt
```txt
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
python-multipart==0.0.9
httpx==0.27.2
```

### Variables del backend
- `DATA_MODE=JSON` (default) — futuro: `SUPABASE`
- `PRODUCTS_FILE=data/products.json`
- `PAYMENT_LINK_TEMPLATE="https://example.com/checkout/football-shop?mode=test&amount={amount}&order_id={order_id}"`

### Levantar el backend
```bash
cd api
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload  # http://localhost:8000
```

### Endpoints principales
- **GET `/health`** → `{"ok": true}`
- **GET `/v1/products`**  
  Query: `q`, `category`, `limit`, `offset`  
  Respuesta: `{ items: Product[], count: number }`  
  Headers: `ETag`, `Cache-Control` (para clientes con red inestable)
- **GET `/v1/products/{id}`** → detalle del producto
- **POST `/v1/pricing/quote`** → calcula **subtotal/discount/shipping/total**  
  Body:
  ```json
  {
    "items": [{"id":"kit-rm-home-24","qty":2},{"id":"ball-fifa-quality-pro","qty":1}],
    "coupon": "HOLA10",
    "delivery_city": "Bogota",
    "delivery_method": "standard"
  }
  ```
- **GET `/v1/payment/link?amount=123000&order_id=XYZ`** → `{ "url": "..." }`

---

## 🔁 Integración Front ↔ API

### 1) Configurar el front
`.env` (frontend):
```env
VITE_API_URL=http://localhost:8000
```

### 2) Fetch de productos con fallback
Ejemplo de `useEffect` en tu `ShopApp.tsx`:
```ts
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

useEffect(() => {
  let cancelled = false
  const load = async () => {
    try {
      const params = new URLSearchParams()
      if (q) params.set('q', q)
      if (cat && cat !== 'Todos') params.set('category', cat)
      const res = await fetch(`${API_URL}/v1/products?${params.toString()}`)
      if (!res.ok) throw new Error('API error')
      const data = await res.json()
      if (!cancelled) setProducts((data?.items ?? []) as ProdEx[])
    } catch {
      // Fallback local
      const resLocal = await fetch('/products.json', { cache: 'no-store' })
      const local = await resLocal.json()
      if (!cancelled) setProducts(local as ProdEx[])
    }
  }
  load()
  return () => { cancelled = true }
}, [q, cat])
```

### 3) Cotización de carrito vía API (opcional)
```ts
const quote = await fetch(`${API_URL}/v1/pricing/quote`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    items: cart.items.map(i => ({ id: i.id, qty: i.qty })),
    coupon: cart.coupon,
    delivery_city: 'Bogota',
    delivery_method: 'standard'
  })
}).then(r => r.json())

// quote.total → úsalo para el botón “Pagar ahora” si quieres exactitud backend
```

### 4) Link de pago
```ts
const link = await fetch(`${API_URL}/v1/payment/link?amount=${quote.total}&order_id=${Date.now()}`)
  .then(r => r.json())
// window.open(link.url, '_blank')
```

---

## 🧭 Roadmap (backend)
- `ProductsRepoSupabase` para leer desde Postgres (SELECT público).
- `POST /v1/orders` + `order_items` para registrar compras (aunque el pago sea externo).
- `profiles` (nombre/avatar) y roles simples.
