from fastapi import FastAPI, Depends, Query, Response, Header, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from .config import DATA_MODE, SUPABASE_URL, SUPABASE_SERVICE_ROLE, API_PUBLIC_URL, FRONT_RETURN_URL
from .repository import ProductsRepoJSON
from .repository_supabase import SupabaseRepo
from .models import QuoteIn, Product
from .services import make_quote

app = FastAPI(title="Football Shop API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

def get_repo():
    if DATA_MODE.upper() == "SUPABASE":
        return SupabaseRepo(SUPABASE_URL, SUPABASE_SERVICE_ROLE)
    return ProductsRepoJSON()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/v1/products")
def products_list(
    response: Response,
    q: Optional[str] = Query(None), category: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0),
    if_none_match: Optional[str] = Header(None, alias="If-None-Match"),
    repo = Depends(get_repo)
):
    if isinstance(repo, ProductsRepoJSON):
        etag = repo.etag()
        if if_none_match == etag:
            response.status_code = 304
            return
        items = repo.list(q=q, category=category, limit=limit, offset=offset)
        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = "public, max-age=300, stale-while-revalidate=120"
        return {"items": [i.dict() for i in items], "count": len(items)}
    else:
        items = repo.products_list(q, category, limit, offset)
        return {"items": items, "count": len(items)}

@app.post("/v1/products")
def product_create(payload: dict, repo = Depends(get_repo)):
    assert isinstance(repo, SupabaseRepo), "CRUD sólo disponible en SUPABASE"
    return repo.product_create(payload)

@app.patch("/v1/products/{pid}")
def product_update(pid: str, payload: dict, repo = Depends(get_repo)):
    assert isinstance(repo, SupabaseRepo), "CRUD sólo disponible en SUPABASE"
    return repo.product_update(pid, payload)

@app.delete("/v1/products/{pid}", status_code=204)
def product_delete(pid: str, repo = Depends(get_repo)):
  if not isinstance(repo, SupabaseRepo):
    raise HTTPException(status_code=400, detail="CRUD solo disponible en SUPABASE")
  repo.product_delete(pid)
  return Response(status_code=204)

@app.post("/v1/checkout/start")
def checkout_start(payload: QuoteIn, repo = Depends(get_repo)):
    if isinstance(repo, ProductsRepoJSON):
        products = repo.list(limit=9999)  
    else:
        rows = repo.products_list(None, None, 1000, 0) 
        products = [Product(**row) for row in rows]     

    quote = make_quote([i.dict() for i in payload.items], products, payload)

    order = {
      "email": None,
      "delivery_city": payload.delivery_city,
      "delivery_method": payload.delivery_method,
      "coupon": payload.coupon,
      "subtotal": quote.subtotal,
      "discount": quote.discount,
      "shipping": quote.shipping,
      "total": quote.total,
      "status": "pending"
    }
    items = [{
      "product_id": it["id"],
      "name": it["name"],
      "unit_price": it["unit_price"],
      "qty": it["qty"],
      "line": it["line"]
    } for it in quote.items]

    if isinstance(repo, SupabaseRepo):
        row = repo.order_create(order, items)
        order_id = row["id"]
    else:
        import uuid
        order_id = str(uuid.uuid4())

    if isinstance(repo, SupabaseRepo):
        sess = repo.payment_session_create(order_id, quote.total, FRONT_RETURN_URL)
        session_id = sess["id"]
    else:
        import uuid
        session_id = str(uuid.uuid4())

    payment_url = f"{API_PUBLIC_URL}/mockpay/{session_id}?order_id={order_id}&return={FRONT_RETURN_URL}"
    return {"order_id": order_id, "session_id": session_id, "payment_url": payment_url}


from fastapi.responses import HTMLResponse

@app.get("/mockpay/{session_id}")
def mockpay_page(
    session_id: str,
    order_id: Optional[str] = None,
    return_: Optional[str] = Query(None, alias="return")
):
    ret = return_ or FRONT_RETURN_URL

    html = f"""
    <!doctype html>
    <html lang="es">
    <head>
      <meta charset="utf-8" />
      <title>MockPay · Pasarela de pruebas</title>
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <style>
        :root {{
          --bg: #050807;
          --card: #0f1814;
          --accent: #1db954;
          --accent-soft: rgba(29,185,84,0.15);
          --danger: #e53935;
          --text: #f5fff7;
          --muted: #9fb0a4;
          --border: #1f2a24;
          --radius: 16px;
          --shadow: 0 18px 45px rgba(0,0,0,0.65);
          --font: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text",
                   "Segoe UI", sans-serif;
        }}
        * {{ box-sizing: border-box; }}
        body {{
          margin: 0;
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: var(--font);
          background: radial-gradient(circle at top, #11251a 0, #050807 55%);
          color: var(--text);
        }}
        .shell {{
          width: 100%;
          max-width: 460px;
          padding: 24px;
        }}
        .card {{
          background: var(--card);
          border-radius: var(--radius);
          border: 1px solid var(--border);
          box-shadow: var(--shadow);
          padding: 24px 22px 20px;
          position: relative;
          overflow: hidden;
        }}
        .badge-env {{
          position: absolute;
          top: 14px;
          right: 18px;
          font-size: 11px;
          letter-spacing: .12em;
          text-transform: uppercase;
          color: var(--accent);
          background: rgba(0,0,0,0.45);
          border-radius: 999px;
          padding: 4px 9px;
          border: 1px solid rgba(29,185,84,0.35);
        }}
        h1 {{
          margin: 0 0 8px;
          font-size: 22px;
          display: flex;
          align-items: center;
          gap: 8px;
        }}
        h1 span.logo {{
          width: 26px;
          height: 26px;
          border-radius: 9px;
          background: radial-gradient(circle at 20% 0, #4cff9a 0, #1db954 35%, #0a381c 80%);
          display: inline-flex;
          align-items: center;
          justify-content: center;
          font-size: 15px;
          box-shadow: 0 0 0 2px rgba(0,0,0,0.45);
        }}
        .subtitle {{
          margin: 0 0 10px;
          font-size: 13px;
          color: var(--muted);
        }}
        .warning {{
          background: #271414;
          border-radius: 10px;
          border: 1px solid rgba(229,57,53,0.4);
          padding: 10px 11px;
          font-size: 12px;
          color: #ffcdd2;
          display: flex;
          gap: 8px;
          align-items: flex-start;
          margin-bottom: 12px;
        }}
        .warning strong {{ display: block; font-size: 12px; }}
        .meta {{
          font-size: 13px;
          color: var(--muted);
          display: grid;
          gap: 4px;
          margin-bottom: 14px;
        }}
        .meta span.label {{ color: #6f8377; }}
        .meta-code {{
          font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
          font-size: 12px;
          padding: 4px 8px;
          border-radius: 7px;
          background: rgba(0,0,0,0.45);
          border: 1px solid var(--border);
          color: #c5f2d7;
          max-width: 100%;
          overflow-wrap: anywhere;
        }}
        form {{
          margin-top: 16px;
          display: flex;
          gap: 10px;
        }}
        button {{
          cursor: pointer;
          border-radius: 999px;
          border: none;
          font-size: 14px;
          padding: 9px 16px;
          font-weight: 500;
          display: inline-flex;
          align-items: center;
          justify-content: center;
        }}
        button.primary {{
          background: var(--accent);
          color: #041007;
        }}
        button.primary:hover {{
          background: #1ee666;
        }}
        button.ghost {{
          background: transparent;
          color: #ffb3b1;
          border: 1px solid rgba(229,57,53,0.55);
        }}
        button.ghost:hover {{
          background: rgba(229,57,53,0.08);
        }}
        .footer-note {{
          margin-top: 14px;
          font-size: 11px;
          color: var(--muted);
          line-height: 1.5;
        }}
        .footer-note strong {{ color: #e0f2e9; }}
        @media (max-width: 520px) {{
          .shell {{ padding: 16px; }}
          .card {{ padding: 20px 16px 16px; }}
          form {{ flex-direction: column; }}
          button {{ width: 100%; }}
        }}
      </style>
    </head>
    <body>
      <div class="shell">
        <div class="card">
          <div class="badge-env">Sandbox</div>
          <h1>
            <span class="logo">⚽</span>
            MockPay · Pasarela de pruebas
          </h1>
          <p class="subtitle">
            Estás simulando un pago para <strong>The Football Shop</strong>.
          </p>

          <div class="warning">
            <span>⚠️</span>
            <div>
              <strong>Pasarela ficticia solo para uso académico.</strong>
              No ingreses datos reales de tarjetas ni información sensible. El resultado de este flujo
              es únicamente una simulación de pago para pruebas.
            </div>
          </div>

          <div class="meta">
            <div>
              <span class="label">ID de sesión</span>
              <div class="meta-code">{session_id}</div>
            </div>
            <div>
              <span class="label">ID de orden</span>
              <div class="meta-code">{order_id or 'No disponible'}</div>
            </div>
          </div>

          <form method="POST" action="/v1/payment/mock/submit">
            <input type="hidden" name="session_id" value="{session_id}" />
            <input type="hidden" name="order_id" value="{order_id or ''}" />
            <input type="hidden" name="return" value="{ret}" />
            <button class="primary" name="action" value="approve">
              Aprobar pago
            </button>
            <button class="ghost" name="action" value="reject">
              Rechazar pago
            </button>
          </form>

          <p class="footer-note">
            Esta pantalla emula el comportamiento de una pasarela de pago real (aprobado / rechazado),
            pero <strong>no procesa cobros reales</strong>. Al continuar, serás redirigido de vuelta a la aplicación.
          </p>
        </div>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(html)

from datetime import datetime
from uuid import uuid4
from fastapi.responses import RedirectResponse

@app.post("/v1/payment/mock/submit")
def mockpay_submit(
    session_id: str = Form(...),
    order_id: Optional[str] = Form(None),
    action: str = Form(...),
    return_: str = Form(..., alias="return"),
    repo = Depends(get_repo)
):
    status = "approved" if action == "approve" else "rejected"

    if isinstance(repo, SupabaseRepo):
        repo.payment_session_update(session_id, status)
        if order_id:
            if status == "approved":
                receipt = f"FS-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid4())[:8]}"
                paid_at = datetime.utcnow().isoformat()
                repo.order_update_status(order_id, "paid",
                                         receipt_code=receipt,
                                         paid_at=paid_at)
            else:
                repo.order_update_status(order_id, "rejected")

    url = f"{return_}?status={'success' if status=='approved' else 'failed'}&order_id={order_id or ''}"
    return RedirectResponse(url, status_code=302)

@app.post("/v1/pricing/quote")
def pricing_quote(payload: QuoteIn, repo = Depends(get_repo)):
    if isinstance(repo, ProductsRepoJSON):
        products = repo.list(limit=9999)  
    else:
        rows = repo.products_list(None, None, 1000, 0)   
        products = [Product(**row) for row in rows]       

    return make_quote([i.dict() for i in payload.items], products, payload)

@app.get("/v1/orders/{order_id}")
def get_order(order_id: str, repo = Depends(get_repo)):
    if not isinstance(repo, SupabaseRepo):
        raise HTTPException(status_code=400, detail="Orders solo disponibles en modo SUPABASE")
    data = repo.order_with_items(order_id)
    if not data:
        raise HTTPException(status_code=404, detail="Order not found")
    return data