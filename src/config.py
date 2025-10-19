import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# ⚙️ MODES
# You can choose per-source modes:
# INTERNAL_MODE = mock | mongo | sql
# GATEWAY_MODE = mock | paystack
# ============================================================
INTERNAL_MODE = os.getenv("INTERNAL_MODE", "mock")   # internal data source
GATEWAY_MODE = os.getenv("GATEWAY_MODE", "mock")     # gateway data source

# ============================================================
# 🗂️ PATHS & REPORTS
# ============================================================
INTERNAL_DATA_PATH = "data/internal_transactions.csv"
GATEWAY_DATA_PATH = "data/gateway_transactions.csv"
REPORT_DIR = "reports"
REPORT_PATH = os.path.join(REPORT_DIR, "reconciliation_report.csv")

# ============================================================
# 🧠 AI CONFIG
# ============================================================
USE_AI = os.getenv("USE_AI", "False").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ============================================================
# 🧾 DATABASE CONFIG
# ============================================================
SQL_DB_URI = os.getenv("SQL_DB_URI", "postgresql://username:password@localhost:5432/fintech_db")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "fintech_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "transactions")

# ============================================================
# 💳 GATEWAY CONFIG
# ============================================================
PAYSTACK_API_URL = os.getenv("PAYSTACK_API_URL", "https://api.paystack.co/transaction")
PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET", "sk_test_dummy")

# ============================================================
# 💳 STRIPE CONFIG
# ============================================================
STRIPE_API_URL = os.getenv("STRIPE_API_URL", "https://api.stripe.com/v1/charges")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_dummy")

# ============================================================
# 💬 SLACK CONFIG
# ============================================================
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
USE_SLACK = os.getenv("USE_SLACK", "False").lower() == "true"


# ============================================
# 🔄 GATEWAY FIELD MAPPINGS
# ============================================
GATEWAY_MAPPINGS = {
    "paystack": {
        "id": "tx_id",
        "amount": "amount",
        "status": "status",
        "currency": "currency",
        "created_at": "created_at",
    },
    "stripe": {
        "id": "tx_id",
        "amount": "amount",
        "status": "status",
        "currency": "currency",
        "created": "created_at",
    },
    # you can add more later:
    # "flutterwave": { ... }
}

# =====================================================
# 🧭 INTERNAL FIELD MAPPING (Dynamic)
# Map your DB or CSV field names → standard names
# =====================================================
INTERNAL_FIELD_MAPPING = {
    "transaction_id": "tx_id",
    "amount_value": "amount",
    "status": "status",
    "currency_code": "currency",
    "created_on": "created_at",
}