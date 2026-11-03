import os
import sys

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your_default_api_key")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "100.95.220.1"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "dbname": os.getenv("DB_CONECTION", "athena"),
}