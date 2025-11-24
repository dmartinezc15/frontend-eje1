import os
from dotenv import load_dotenv
load_dotenv()

PRODUCTS_FILE = os.getenv("PRODUCTS_FILE", "data/products.json")
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
DATA_MODE = os.getenv("DATA_MODE", "JSON")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE", "")
API_PUBLIC_URL = os.getenv("API_PUBLIC_URL", "http://localhost:8000")
FRONT_RETURN_URL = os.getenv("FRONT_RETURN_URL", "http://localhost:5173/checkout/return")