from fastapi import FastAPI, Depends, Header, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from .repository import ProductsRepoJSON
from .models import QuoteIn, PaymentLinkOut
from .services import make_quote
from .config import PAYMENT_LINK_TEMPLATE

app = FastAPI(title="Football Shop API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

def get_repo():
    # Por ahora JSON; luego cambiamos por DATA_MODE
    return ProductsRepoJSON()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/v1/products")
def list_products(
    response: Response,
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    if_none_match: Optional[str] = Header(None, alias="If-None-Match"),
    repo: ProductsRepoJSON = Depends(get_repo),
):
    etag = repo.etag()
    # ETag para conexiones inestables
    if if_none_match == etag:
        response.status_code = 304
        return
    items = repo.list(q=q, category=category, limit=limit, offset=offset)
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "public, max-age=300, stale-while-revalidate=120"
    return {"items": [i.dict() for i in items], "count": len(items)}

@app.get("/v1/products/{pid}")
def get_product(pid: str, repo: ProductsRepoJSON = Depends(get_repo)):
    p = repo.get(pid)
    if not p: return {"error": "not_found"}
    return p

@app.post("/v1/pricing/quote")
def pricing_quote(payload: QuoteIn, repo: ProductsRepoJSON = Depends(get_repo)):
    products = repo.list(limit=9999)
    return make_quote([i.dict() for i in payload.items], products, payload)

@app.get("/v1/payment/link", response_model=PaymentLinkOut)
def payment_link(amount: int, order_id: Optional[str] = None):
    url = PAYMENT_LINK_TEMPLATE.format(amount=amount, order_id=order_id or "preview")
    return PaymentLinkOut(url=url)
