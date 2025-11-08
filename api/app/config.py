import os

DATA_MODE = os.getenv("DATA_MODE", "JSON")  # JSON | SUPABASE
PRODUCTS_FILE = os.getenv("PRODUCTS_FILE", "data/products.json")

PAYMENT_LINK_TEMPLATE = os.getenv(
    "PAYMENT_LINK_TEMPLATE",
    "https://example.com/checkout/football-shop?mode=test&amount={amount}&order_id={order_id}"
)

SHIPPING_TABLE = {
    "bogota": {"standard": 9000, "express": 16000},
    "medellin": {"standard": 10000, "express": 18000},
    "cali": {"standard": 11000, "express": 19000},
    "_default": {"standard": 12000, "express": 20000},
}

COUPONS = {
    "HOLA10": {"type": "percent", "value": 10},    
    "ENVIOFREE": {"type": "shipping_free"},        
    "RM-20K": {"type": "amount", "value": 20000},  
}
