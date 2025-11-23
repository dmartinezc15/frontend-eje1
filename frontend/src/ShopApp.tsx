import { useEffect, useMemo, useState } from 'react'
import { useCart, type Product } from './store/cart'
import { supabase } from './lib/supabase'
import './App.css'

type ProdEx = Product & { category?: string }


const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000'

export default function ShopApp() {
  const cart = useCart()
  const [products, setProducts] = useState<ProdEx[]>([])
  const [q, setQ] = useState('')
  const [openCart, setOpenCart] = useState(false)
  const [cat, setCat] = useState<string>('Todos')

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
        try {
          const resLocal = await fetch('/products.json', { cache: 'no-store' })
          const local = await resLocal.json()
          if (!cancelled) setProducts(local as ProdEx[])
        } catch (e) {
          console.error(e)
        }
      }
    }

    load()
    return () => { cancelled = true }
  }, [q, cat])
  useEffect(() => { document.body.style.overflow = openCart ? 'hidden' : 'auto' }, [openCart])
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const status = params.get('status')

    if (status === 'success') {
      cart.clear()
      setOpenCart(false)
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }, [cart])

  const categories = useMemo(() => ['Todos', ...Array.from(new Set(products.map(p => p.category || 'Otros')))], [products])

  const filtered = useMemo(() => {
    const byCat = cat === 'Todos' ? products : products.filter(p => p.category === cat)
    const s = q.trim().toLowerCase()
    return s ? byCat.filter(p => p.name.toLowerCase().includes(s) || (p.category||'').toLowerCase().includes(s)) : byCat
  }, [products, q, cat])

  const itemsCount = cart.items.reduce((a, i) => a + i.qty, 0)

  const waText = useMemo(() => {
    const lines = cart.items.map(i => `• ${i.name} x${i.qty} = $${(i.price * i.qty).toLocaleString()}`)
    return `Pedido:%0A${lines.join('%0A')}${cart.coupon ? `%0ACupón: ${cart.coupon}` : ''}%0ATotal: $${cart.total().toLocaleString()}`
  }, [cart.items, cart.coupon])

  const waLink = `https://wa.me/573136833122?text=${waText}`

  async function startCheckout() {
    try {
      const body = {
        items: cart.items.map(i => ({ id: i.id, qty: i.qty })),
        coupon: cart.coupon || null,
        delivery_city: 'Bogota',
        delivery_method: 'standard'
      }

      const res = await fetch(`${API_URL}/v1/checkout/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })

      if (!res.ok) throw new Error('Error en checkout')

      const data = await res.json()

      if (data?.payment_url) {
        // Redirige a la pasarela ficticia
        window.location.href = data.payment_url
      } else {
        // fallback: abre WhatsApp si algo raro pasa
        window.open(waLink, '_blank')
      }
    } catch (e) {
      console.error(e)
      window.open(waLink, '_blank')
    }
  }

  return (
    <>
      <div className="container">
        <header className="topbar">
          <button className="ghost" onClick={() => supabase.auth.signOut()}>
            Cerrar sesión
          </button>
          <h1>The Football Shop</h1>
          <div className="actions">
            <input placeholder="Buscar producto o categoría…" value={q} onChange={e => setQ(e.target.value)} />
            <button className="cart-pill" onClick={() => setOpenCart(true)}>
              🛒 {itemsCount} ítems — <strong>${cart.total().toLocaleString()}</strong>
            </button>
            <button className="ghost" onClick={() => cart.clear()}>Vaciar</button>
          </div>
        </header>

        <section className="hero">
          <div className="hero-content">
            <h2>Equipaciones 24/25</h2>
            <p>Personaliza con tu nombre y número. Envíos a todo el país.</p>
            <button
              className="primary"
              onClick={() => { setCat('Ropa'); document.getElementById('grid')?.scrollIntoView({ behavior: 'smooth' }) }}
            >
              Ver camisetas
            </button>
          </div>
        </section>
        <div className="chips">
          {categories.map(c => (
            <button key={c} className={`chip ${cat === c ? 'active' : ''}`} onClick={() => setCat(c)}>
              {c}
            </button>
          ))}
        </div>

        <section id="grid" className="grid centered wide">
          {filtered.map(p => (
            <article key={p.id} className="card pro">
              <div className="thumb ar-4-3">
                {p.img ? <img src={p.img} alt={p.name} /> : <div className="ph" />}
              </div>
              <h3>{p.name}</h3>
              <div className="muted">{p.category}</div>
              <div className="price">${p.price.toLocaleString()}</div>
              <button onClick={() => cart.add(p)} className="primary">Añadir</button>
            </article>
          ))}
        </section>

        {/* Ventajas */}
        <section className="tiles">
          <div className="tile"><span>🚚</span><b>Envío 24–72h</b><small>Cobertura nacional</small></div>
          <div className="tile"><span>🔄</span><b>Devolución 7 días</b><small>Cambios por talla</small></div>
          <div className="tile"><span>🛡️</span><b>Pago seguro</b><small>Links oficiales</small></div>
          <div className="tile"><span>🎯</span><b>Stock verificado</b><small>Actualizado al día</small></div>
        </section>

        <footer className="footer">
          <div>© {new Date().getFullYear()} The Football Shop — Fútbol y más.</div>
          <div className="muted">Precios en COP. Imágenes ilustrativas.</div>
        </footer>
      </div>

      <button className="fab" onClick={() => setOpenCart(true)}>🛒 {itemsCount}</button>

      {cart.items.length > 0 && (
        <div className="checkout-bar">
          <div className="cb-info">
            <strong>{itemsCount}</strong> ítems <span className="dot" />
            Total <strong>${cart.total().toLocaleString()}</strong>
          </div>
          <div className="cb-actions">
            <button className="ghost" onClick={() => setOpenCart(true)}>Ver carrito</button>
            <button className="primary" onClick={startCheckout}>
              Pagar ahora
            </button>
            <button className="ghost" onClick={() => window.open(waLink, '_blank')}>
              Pagar por WhatsApp
            </button>
          </div>
        </div>
      )}

      <div className={`overlay ${openCart ? 'show' : ''}`} onClick={() => setOpenCart(false)} />
      <aside className={`drawer side ${openCart ? 'open' : ''}`}>
        <div className="drawer-head">
          <h2>Carrito</h2>
          <button className="ghost" onClick={() => setOpenCart(false)}>Cerrar ✕</button>
        </div>

        {cart.items.length === 0 ? (
          <div className="muted">Tu carrito está vacío.</div>
        ) : (
          <>
            {cart.items.map(i => (
              <div key={i.id} className="row">
                <div className="info">
                  <div className="name">{i.name}</div>
                  <div className="muted">${(i.price * i.qty).toLocaleString()}</div>
                </div>
                <div className="qty">
                  <input type="number" min={1} value={i.qty}
                    onChange={e => cart.setQty(i.id, Number(e.target.value))} />
                  <button className="link danger" onClick={() => cart.remove(i.id)}>Quitar</button>
                </div>
              </div>
            ))}

            <div className="coupon">
              <input placeholder="Cupón (ej: HOLA10)" onChange={e => cart.setCoupon(e.target.value)} />
            </div>

            <div className="totals">
              <div className="line"><span>Subtotal</span><strong>${cart.subtotal().toLocaleString()}</strong></div>
              <div className="line"><span>Total</span><strong>${cart.total().toLocaleString()}</strong></div>
            </div>

            <button className="primary block xl" onClick={startCheckout}>
              Pagar ahora
            </button>
            <button className="ghost" onClick={() => window.open(waLink, '_blank')}>
              Pagar por WhatsApp
            </button>
          </>
        )}
      </aside>
    </>
  )
}
