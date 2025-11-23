from fastapi import FastAPI, Depends, Query, Response, Header
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

@app.delete("/v1/products/{pid}")
def product_delete(pid: str, repo = Depends(get_repo)):
    assert isinstance(repo, SupabaseRepo), "CRUD sólo disponible en SUPABASE"
    repo.product_delete(pid)
    return {"ok": True}

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


@app.get("/mockpay/{session_id}")
def mockpay_page(session_id: str, order_id: Optional[str] = None, return_: Optional[str] = Query(None, alias="return")):
    ret = return_ or FRONT_RETURN_URL
    html = f"""
    <html><head><meta charset="utf-8"><title>MockPay</title></head>
    <body style="font-family:system-ui;padding:24px;background:#0b0f0c;color:#e6f4ea">
      <h2>MockPay — Pago de orden</h2>
      <p>Orden: <b>{order_id or '-'}</b></p>
      <p>Sesión: <b>{session_id}</b></p>
      <form method="POST" action="/v1/payment/mock/submit" style="display:flex;gap:8px;margin-top:16px">
        <input type="hidden" name="session_id" value="{session_id}" />
        <input type="hidden" name="order_id" value="{order_id or ''}" />
        <input type="hidden" name="return" value="{ret}" />
        <button name="action" value="approve">Aprobar</button>
        <button name="action" value="reject">Rechazar</button>
      </form>
    </body></html>
    """
    from fastapi.responses import HTMLResponse
    return HTMLResponse(html)

from fastapi import Form
from fastapi.responses import RedirectResponse

@app.post("/v1/payment/mock/submit")
def mockpay_submit(session_id: str = Form(...), order_id: Optional[str] = Form(None),
                   action: str = Form(...), return_: str = Form(..., alias="return"),
                   repo = Depends(get_repo)):
    status = "approved" if action == "approve" else "rejected"
    if isinstance(repo, SupabaseRepo):
        repo.payment_session_update(session_id, status)
        if order_id:
            repo.order_update_status(order_id, "paid" if status == "approved" else "rejected")
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