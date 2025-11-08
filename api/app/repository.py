import json, hashlib
from typing import List, Optional
from .models import Product
from .config import PRODUCTS_FILE

class ProductsRepoJSON:
    def __init__(self, path: str = PRODUCTS_FILE):
        self.path = path
        self._cache = None
        self._etag = None
        self._load()

    def _load(self):
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._cache = [Product(**p) for p in data]
        canon = json.dumps(data, ensure_ascii=False, sort_keys=True).encode()
        self._etag = hashlib.md5(canon).hexdigest()

    def etag(self) -> str:
        return self._etag

    def list(self, q: Optional[str] = None, category: Optional[str] = None,
             limit: int = 50, offset: int = 0) -> List[Product]:
        items = self._cache
        if category:
            items = [p for p in items if (p.category or "").lower() == category.lower()]
        if q:
            ql = q.lower()
            items = [p for p in items if ql in p.name.lower() or ql in (p.category or "").lower()]
        return items[offset: offset + limit]

    def get(self, pid: str) -> Optional[Product]:
        for p in self._cache:
            if p.id == pid:
                return p
        return None
