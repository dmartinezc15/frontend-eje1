import httpx
from typing import Optional, List, Dict, Any

class SupabaseRepo:
    def __init__(self, url: str, key: str):
        self.base = f"{url.rstrip('/')}/rest/v1"
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Prefer": "return=representation"
        }

    # ===== PRODUCTS =====
    def products_list(self, q: Optional[str], category: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
        params = {"select":"*", "order":"name.asc", "limit":limit, "offset":offset}
        if category: params["category"] = f"eq.{category}"
        if q: params["or"] = f"(name.ilike.*{q}*,category.ilike.*{q}*)"
        with httpx.Client(timeout=10.0) as c:
            r = c.get(f"{self.base}/products", headers=self.headers, params=params)
            r.raise_for_status()
            return r.json()

    def product_get(self, pid: str) -> Optional[Dict[str, Any]]:
        with httpx.Client(timeout=10.0) as c:
            r = c.get(f"{self.base}/products", headers=self.headers, params={"select":"*","id":f"eq.{pid}"})
            r.raise_for_status()
            arr = r.json()
            return arr[0] if arr else None

    def product_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        with httpx.Client(timeout=10.0) as c:
            r = c.post(f"{self.base}/products", headers=self.headers, json=payload)
            r.raise_for_status()
            return r.json()[0]

    def product_update(self, pid: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        with httpx.Client(timeout=10.0) as c:
            r = c.patch(f"{self.base}/products", headers=self.headers, params={"id":f"eq.{pid}"}, json=payload)
            r.raise_for_status()
            return r.json()[0]

    def product_delete(self, pid: str) -> None:
        with httpx.Client(timeout=10.0) as c:
            r = c.delete(f"{self.base}/products", headers=self.headers, params={"id":f"eq.{pid}"})
            r.raise_for_status()

    # ===== ORDERS & PAYMENTS =====
    def order_create(self, order: Dict[str, Any], items: List[Dict[str, Any]]) -> Dict[str, Any]:
        with httpx.Client(timeout=10.0) as c:
            ro = c.post(f"{self.base}/orders", headers=self.headers, json=order); ro.raise_for_status()
            row = ro.json()[0]
            for it in items:
                it["order_id"] = row["id"]
            ri = c.post(f"{self.base}/order_items", headers=self.headers, json=items); ri.raise_for_status()
            return row

    def payment_session_create(self, order_id: str, amount: int, return_url: str) -> Dict[str, Any]:
        with httpx.Client(timeout=10.0) as c:
            r = c.post(f"{self.base}/payment_sessions", headers=self.headers,
                       json={"order_id": order_id, "amount": amount, "return_url": return_url})
            r.raise_for_status()
            return r.json()[0]

    def payment_session_update(self, session_id: str, status: str):
        with httpx.Client(timeout=10.0) as c:
            r = c.patch(f"{self.base}/payment_sessions",
                        headers=self.headers, params={"id":f"eq.{session_id}"},
                        json={"status": status})
            r.raise_for_status()

    def order_update_status(self, order_id: str, status: str,
                            receipt_code: str | None = None,
                            paid_at: str | None = None):
        payload: dict[str, Any] = {"status": status}
        if receipt_code is not None:
            payload["receipt_code"] = receipt_code
        if paid_at is not None:
            payload["paid_at"] = paid_at

        with httpx.Client(timeout=10.0) as c:
            r = c.patch(
                f"{self.base}/orders",
                headers=self.headers,
                params={"id": f"eq.{order_id}"},
                json=payload
            )
            r.raise_for_status()
    
    def order_with_items(self, order_id: str) -> dict | None:
        with httpx.Client(timeout=10.0) as c:
            r = c.get(
                f"{self.base}/orders",
                headers=self.headers,
                params={
                    "select": "*,order_items(*)",
                    "id": f"eq.{order_id}"
                }
            )
            r.raise_for_status()
            arr = r.json()
            return arr[0] if arr else None