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
- **Node.js 24+**
- **npm**

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

---
### C) Docker (Nginx)
```dockerfile
# Build
FROM node:20-alpine AS build
WORKDIR /app
COPY . .
RUN corepack enable && pnpm i && pnpm build

# Serve
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```
```bash
docker build -t football-shop .
docker run -p 8080:80 football-shop
# http://localhost:8080
```

> Despliegue bajo subruta (p.ej. `/tienda/`): en `vite.config.ts` ajusta `base: '/tienda/'`.

---

## 🔧 Troubleshooting
- **No carga `products.json`** → verifícalo en `public/` y que la ruta sea `/products.json`.
- **Imágenes no visibles** → coloca archivos en `public/img/` y usa rutas `/img/...`.
- **“Pagar ahora” abre WhatsApp** → define `VITE_PAYMENT_LINK` en `.env` y reinicia Vite.
- **Estado no persiste** → limpia `localStorage` o revisa permisos del navegador.

---

## 🗺️ Roadmap (sin backend)
- Selector de **tallas** y **variantes** en tarjeta y carrito.
- **Cupones** por % o valor fijo.
- **Compartir carrito** por URL.
- **PWA offline** con `vite-plugin_pwa`.
- Exportar pedido en **PDF/JSON**.
