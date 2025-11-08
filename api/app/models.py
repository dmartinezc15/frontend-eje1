from pydantic import BaseModel, Field
from typing import List, Optional, Any

class Product(BaseModel):
    id: str
    name: str
    price: int
    img: Optional[str] = None
    category: Optional[str] = None
    club: Optional[str] = None
    league: Optional[str] = None
    season: Optional[str] = None
    variant: Optional[Any] = None
    sizes: Optional[Any] = None
    stock: Optional[int] = 0
    tags: Optional[list[str]] = None
    rating: Optional[float] = None
    sku: Optional[str] = None

class QuoteItemIn(BaseModel):
    id: str
    qty: int = Field(gt=0)

class QuoteIn(BaseModel):
    items: List[QuoteItemIn]
    coupon: Optional[str] = None
    delivery_city: Optional[str] = "bogota"
    delivery_method: Optional[str] = "standard"  # standard | express

class QuoteOut(BaseModel):
    items: List[dict]
    subtotal: int
    discount: int
    shipping: int
    total: int
    warnings: List[str] = []
    applied_coupon: Optional[str] = None

class PaymentLinkOut(BaseModel):
    url: str
