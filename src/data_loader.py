# ==============================================
# src/data_loader.py
# ----------------------------------------------
# Handles loading internal and gateway transaction data
# Supports: CSV (mock), MongoDB, SQL, Paystack, and Stripe
# Uses dynamic field mappings from config.py
# ==============================================

import pandas as pd
import requests
from sqlalchemy import create_engine
from pymongo import MongoClient
from src.utils.logger import setup_logger
from src.config import (
    INTERNAL_MODE,
    GATEWAY_MODE,
    INTERNAL_DATA_PATH,
    GATEWAY_DATA_PATH,
    SQL_DB_URI,
    MONGO_URI,
    MONGO_DB,
    MONGO_COLLECTION,
    PAYSTACK_API_URL,
    PAYSTACK_SECRET,
    STRIPE_API_URL,
    STRIPE_SECRET_KEY,
    GATEWAY_MAPPINGS,
    INTERNAL_FIELD_MAPPING,  
)

logger = setup_logger()


# =====================================================
# 🔄 Helper — Apply internal field mappings dynamically
# =====================================================
def normalize_internal_data(df):
    """
    Dynamically rename internal fields based on INTERNAL_FIELD_MAPPING in config.py.
    """
    if not INTERNAL_FIELD_MAPPING:
        logger.warning("⚠️ No INTERNAL_FIELD_MAPPING found. Using raw field names.")
        return df

    df = df.rename(columns=INTERNAL_FIELD_MAPPING)
    return df


# =====================================================
# Load INTERNAL data (your own app transactions)
# =====================================================
def load_internal_data():
    """
    Load internal transactions for reconciliation.
    Modes:
        - mock   → from CSV
        - mongo  → from MongoDB
        - sql    → from PostgreSQL or MySQL
    """

    if INTERNAL_MODE == "mock":
        logger.info("📂 Loading internal data from mock CSV...")
        df = pd.read_csv(INTERNAL_DATA_PATH)
        df = normalize_internal_data(df)
        logger.info(f"✅ Loaded {len(df)} internal records from mock CSV.")
        return df

    elif INTERNAL_MODE == "mongo":
        logger.info("🗄️ Loading internal data from MongoDB...")
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]

        # Automatically build projection from mapping keys
        projection = {key: 1 for key in INTERNAL_FIELD_MAPPING.keys()}
        projection["_id"] = 0

        data = list(collection.find({}, projection))
        df = pd.DataFrame(data)
        df = normalize_internal_data(df)
        logger.info(f"✅ Loaded {len(df)} internal records from MongoDB.")
        return df

    elif INTERNAL_MODE == "sql":
        logger.info("🗃️ Loading internal data from SQL database...")
        engine = create_engine(SQL_DB_URI)

        # Auto-select only columns in mapping
        selected_fields = ", ".join(INTERNAL_FIELD_MAPPING.keys())
        query = f"SELECT {selected_fields} FROM transactions"
        df = pd.read_sql(query, engine)

        df = normalize_internal_data(df)
        logger.info(f"✅ Loaded {len(df)} internal records from SQL.")
        return df

    else:
        logger.error(f"❌ Unsupported INTERNAL_MODE: {INTERNAL_MODE}")
        return pd.DataFrame()


# =====================================================
# Helper — Normalize Gateway Data Dynamically
# =====================================================
def normalize_gateway_data(df, gateway_name):
    """
    Dynamically rename fields based on GATEWAY_MAPPINGS in config.py.
    """
    mapping = GATEWAY_MAPPINGS.get(gateway_name, {})
    if not mapping:
        logger.warning(f"⚠️ No mapping found for {gateway_name}. Using raw field names.")
        return df

    df = df.rename(columns=mapping)
    return df


# =====================================================
# Load GATEWAY data (external payment provider)
# =====================================================
def load_gateway_data():
    """
    Load payment gateway transactions for reconciliation.
    Modes:
        - mock     → from CSV
        - paystack → from Paystack API
        - stripe   → from Stripe API
    """

    # 1️⃣ MOCK CSV (for testing)
    if GATEWAY_MODE == "mock":
        logger.info("📂 Loading gateway data from mock CSV...")
        return pd.read_csv(GATEWAY_DATA_PATH)

    # 2️⃣ PAYSTACK API
    elif GATEWAY_MODE == "paystack":
        logger.info("🌍 Fetching transactions from Paystack API...")
        headers = {"Authorization": f"Bearer {PAYSTACK_SECRET}"}
        response = requests.get(PAYSTACK_API_URL, headers=headers)

        if response.status_code != 200:
            logger.error(f"❌ Paystack API failed: {response.status_code}")
            return pd.DataFrame()

        data = response.json().get("data", [])
        df = pd.DataFrame(data)
        df = normalize_gateway_data(df, "paystack")

        # Convert amount from kobo to Naira if applicable
        if "amount" in df.columns:
            df["amount"] = df["amount"].astype(float) / 100

        logger.info(f"✅ Loaded {len(df)} Paystack records.")
        return df

    # 3️⃣ STRIPE API
    elif GATEWAY_MODE == "stripe":
        logger.info("💳 Fetching transactions from Stripe API...")
        headers = {"Authorization": f"Bearer {STRIPE_SECRET_KEY}"}
        response = requests.get(STRIPE_API_URL, headers=headers)

        if response.status_code != 200:
            logger.error(f"❌ Stripe API failed: {response.status_code}")
            return pd.DataFrame()

        data = response.json().get("data", [])
        df = pd.DataFrame(data)
        df = normalize_gateway_data(df, "stripe")

        # Convert amount from cents to dollars if applicable
        if "amount" in df.columns:
            df["amount"] = df["amount"].astype(float) / 100

        logger.info(f"✅ Loaded {len(df)} Stripe records.")
        return df

    else:
        logger.error(f"❌ Unsupported GATEWAY_MODE: {GATEWAY_MODE}")
        return pd.DataFrame()
