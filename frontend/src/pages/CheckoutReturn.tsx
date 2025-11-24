import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useCart } from '../store/cart'

const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000'

type OrderItem = {
  product_id: string
  name: string
  unit_price: number
  qty: number
  line: number
}

type Order = {
  id: string
  receipt_code?: string
  subtotal: number
  discount: number
  shipping: number
  total: number
  status: string
  created_at?: string
  paid_at?: string
  order_items?: OrderItem[]
}

export default function CheckoutReturn() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const cart = useCart()

  const status = searchParams.get('status')
  const orderId = searchParams.get('order_id')
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [seconds, setSeconds] = useState(8)

  // 🧹 Limpiar carrito UNA sola vez si venimos de pago exitoso
  useEffect(() => {
    if (status === 'success') {
      cart.clear()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // <- sin status ni cart, se ejecuta solo al montar

  useEffect(() => {
    if (status !== 'success' || !orderId) {
      setLoading(false)
      return
    }

    const load = async () => {
      try {
        const res = await fetch(`${API_URL}/v1/orders/${orderId}`)
        if (!res.ok) throw new Error('No se encontró la orden')
        const data = await res.json()
        setOrder(data as Order)
      } catch (e: any) {
        setError(e.message || 'Error cargando la orden')
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [status, orderId])

  // contador para volver al inicio
  useEffect(() => {
    const t = setInterval(() => setSeconds(s => s - 1), 1000)
    return () => clearInterval(t)
  }, [])

  useEffect(() => {
    if (seconds <= 0) navigate('/', { replace: true })
  }, [seconds, navigate])

  const goHome = () => navigate('/', { replace: true })

  if (loading) return <div className="center-page">Cargando recibo…</div>

  if (status !== 'success') {
    return (
      <div className="center-page">
        <h2>Pago no completado</h2>
        <p className="muted">Tu pago fue rechazado o cancelado.</p>
        <button className="primary" onClick={goHome}>Volver a la tienda</button>
      </div>
    )
  }

  if (!orderId || error) {
    return (
      <div className="center-page">
        <h2>No se pudo cargar el recibo</h2>
        <p className="muted">{error || 'No se encontró la orden.'}</p>
        <button className="primary" onClick={goHome}>Volver a la tienda</button>
      </div>
    )
  }

  return (
    <div className="center-page">
      <div className="receipt-card">
        <h2>Recibo de compra</h2>
        <p className="muted">Gracias por tu compra en The Football Shop ⚽</p>

        <div className="receipt-meta">
          <div><span>Recibo:</span> <strong>{order?.receipt_code || order?.id}</strong></div>
          <div><span>Estado:</span> <strong>{order?.status}</strong></div>
          {order?.paid_at && (
            <div><span>Pagado:</span> <strong>{new Date(order.paid_at).toLocaleString()}</strong></div>
          )}
        </div>

        <div className="receipt-items">
          {order?.order_items?.map(it => (
            <div key={it.product_id} className="receipt-row">
              <div>
                <div className="name">{it.name}</div>
                <div className="muted">x{it.qty}</div>
              </div>
              <div>${it.line.toLocaleString()}</div>
            </div>
          ))}
        </div>

        <div className="totals">
          <div className="line"><span>Subtotal</span><strong>${order?.subtotal.toLocaleString()}</strong></div>
          <div className="line"><span>Descuento</span><strong>-${order?.discount.toLocaleString()}</strong></div>
          <div className="line"><span>Envío</span><strong>${order?.shipping.toLocaleString()}</strong></div>
          <div className="line total"><span>Total</span><strong>${order?.total.toLocaleString()}</strong></div>
        </div>

        <p className="muted" style={{ marginTop: 8 }}>
          Serás redirigido al inicio en {seconds} segundos…
        </p>
        <button className="primary" onClick={goHome}>Volver ahora</button>
      </div>
    </div>
  )
}
