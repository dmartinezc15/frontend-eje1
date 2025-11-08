from typing import List, Tuple
from .models import Product, QuoteIn, QuoteOut
from .config import COUPONS, SHIPPING_TABLE

def _shipping_cost(city: str, method: str) -> int:
    city_key = city.lower()
    table = SHIPPING_TABLE.get(city_key, SHIPPING_TABLE["_default"])
    return table.get(method, table["standard"])

def _apply_coupon(code: str | None, subtotal: int, shipping: int) -> Tuple[int, int, str | None]:
    if not code: return 0, shipping, None
    c = COUPONS.get(code.upper())
    if not c: return 0, shipping, None
    if c["type"] == "percent":
        return int(subtotal * c["value"] / 100), shipping, code.upper()
    if c["type"] == "amount":
        return min(subtotal, int(c["value"])), shipping, code.upper()
    if c["type"] == "shipping_free":
        return 0, 0, code.upper()
    return 0, shipping, None

def make_quote(items_in: List[dict], products: List[Product], payload: QuoteIn) -> QuoteOut:
    id_map = {p.id: p for p in products}
    items_out, warnings = [], []
    subtotal = 0

    for it in items_in:
        prod = id_map.get(it["id"])
        if not prod:
            warnings.append(f"Producto {it['id']} no existe.")
            continue
        qty = max(1, int(it["qty"]))
        if prod.stock is not None and prod.stock < qty:
            warnings.append(f"Stock insuficiente para {prod.name} (solicitado {qty}, stock {prod.stock}).")
            qty = max(0, prod.stock or 0)
        line = prod.price * qty
        subtotal += line
        items_out.append({
            "id": prod.id, "name": prod.name, "unit_price": prod.price,
            "qty": qty, "line": line, "img": prod.img
        })

    shipping = _shipping_cost(payload.delivery_city or "bogota", payload.delivery_method or "standard")
    discount, shipping, applied = _apply_coupon(payload.coupon, subtotal, shipping)
    total = max(0, subtotal - discount + shipping)
    return QuoteOut(
        items=items_out, subtotal=subtotal, discount=discount,
        shipping=shipping, total=total, warnings=warnings, applied_coupon=applied
    )
