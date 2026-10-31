import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY", "")
NEBIUS_BASE_URL = os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "nvidia/Nemotron-3_5-Lightning")

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "")
PAYPAL_ENV = os.getenv("PAYPAL_ENV", "sandbox")
PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com" if PAYPAL_ENV == "sandbox" else "https://api-m.paypal.com"

PORT = int(os.getenv("PORT", "8010"))
HOST = os.getenv("HOST", "127.0.0.1")
