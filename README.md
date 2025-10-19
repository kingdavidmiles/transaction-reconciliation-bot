# 💸 Automated Transaction Reconciliation System

![Python Version](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Build](https://img.shields.io/badge/Build-Passing-brightgreen.svg)
![Slack](https://img.shields.io/badge/Slack-Connected-blueviolet.svg)

> A smart automation tool that compares **internal transaction records** with **payment gateway data (Paystack, Stripe, etc.)** and automatically reports mismatches, missing transactions, and inconsistencies.  
> Ideal for **Finance**, **QA**, and **DevOps** teams looking to maintain accurate financial records and ensure gateway integrations are working correctly.

---

## 🚀 Overview

The **Automated Transaction Reconciliation System** streamlines financial verification by cross-checking internal transaction data from your systems against external payment gateways like **Paystack** or **Stripe**.

It helps you automatically detect:
- Missing or duplicate transactions  
- Amount or currency mismatches  
- Status inconsistencies  
- Integration or API syncing errors  

You can run it manually, on a schedule, or inside a CI/CD pipeline.  
Reports can be sent to **Slack**, saved as **CSV**, or logged locally.

---

## 🧠 Features

✅ Load internal transaction data from:
- CSV (mock/testing)
- SQL database (PostgreSQL / MySQL)
- MongoDB

✅ Fetch payment gateway data from:
- Paystack API  
- Stripe API  
- Mock CSV (for testing)

✅ Perform:
- Transaction reconciliation  
- Field normalization & mapping  
- Amount and currency validation  
- Status mismatch detection  
- Summary and detailed reports

✅ Notify & Export:
- Slack alerts with reconciliation summaries  
- Local CSV or JSON reports  
- Logs for automation pipelines

---

## 🧩 Architecture Overview

```
                ┌─────────────────────┐
                │ Internal Data Source │
                │ (SQL / Mongo / CSV)  │
                └─────────┬───────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Data Loader      │
                 │ (src/data_loader.py)│
                 └─────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Reconciliation   │
                 │ (compare logic)  │
                 └─────────────────┘
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
     ┌──────────────┐          ┌────────────────┐
     │ Slack Alerts  │          │ CSV / JSON Log │
     └──────────────┘          └────────────────┘
```

---

## ⚙️ Setup Guide

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/transaction-reconciliation-bot.git
cd transaction-reconciliation-bot
```

---

### 2️⃣ Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

Example `requirements.txt` includes:
```
pandas
requests
python-dotenv
sqlalchemy
pymongo
openpyxl
schedule
slack_sdk
```

---

### 4️⃣ Configure Environment Variables

Create a `.env` file in the root directory and fill it like this:

```env
# =====================================
# MODES
# Choose your data sources independently
# =====================================
INTERNAL_MODE=mock     # mock | mongo | sql
GATEWAY_MODE=mock      # mock | paystack | stripe

# =====================================
# AI & SLACK
# =====================================
USE_AI=False
OPENAI_API_KEY=sk-projxxxxxxxxxxx
SLACK_BOT_TOKEN=xoxb-xxxxxxxx
SLACK_CHANNEL_ID=D09xxxxxx
USE_SLACK=True

# =====================================
# DATABASE CONFIG (Mongo + SQL)
# =====================================
SQL_DB_URI=postgresql://username:password@localhost:5432/fintech_db
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=fintech_db
MONGO_COLLECTION=transactions

# =====================================
# PAYSTACK CONFIG
# =====================================
PAYSTACK_SECRET=sk_test_your_secret_key
PAYSTACK_API_URL=https://api.paystack.co/transaction

# =====================================
# STRIPE CONFIG
# =====================================
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_API_URL=https://api.stripe.com/v1/charges


# Logging & Reports
REPORT_PATH=reports/
```

---

## 🧠 Slack Integration

This project sends daily or on-demand reconciliation reports directly to a Slack channel.

### Slack Setup Steps

1. Go to [Slack API Apps](https://api.slack.com/apps)  
2. Click **Create New App** → “From Scratch”  
3. Add these **Bot Token Scopes** under **OAuth & Permissions**:
   - `chat:write`
   - `channels:read`
   - `groups:read`
   - `users:read`
4. Install the app to your workspace  
5. Copy the **Bot User OAuth Token** (looks like `xoxb-...`)  
6. Add it to your `.env` as `SLACK_BOT_TOKEN`
7. Right-click your Slack channel → “View channel details” → “More” → “Copy Channel ID”  
   Add it to `.env` as `SLACK_CHANNEL_ID`

✅ Example Slack Message:
```
🚨 Reconciliation Summary
-----------------------------------
✅ Matched Transactions: 984
⚠️ Missing in Gateway: 12
❌ Status Mismatch: 4
🕒 Timestamp Drift: 3
-----------------------------------
Report saved: reports/summary_2025-10-19.csv
```

---

## 🧾 How to Run

### 1️⃣ Run Once Manually
```bash
python -m src.main
```

### 2️⃣ Run on Schedule (Automatic)
You can schedule it to run periodically using the built-in scheduler:
```bash
python -m src.scheduler
```

This runs reconciliation every hour (you can adjust the schedule inside `src/scheduler.py`).

---

## 🧪 Example Outputs

### ✅ Sample Console Log
```
📂 Loading internal data from SQL...
🌍 Fetching Paystack transactions...
✅ Loaded 1,200 internal records and 1,198 gateway records
⚠️ 2 missing transactions detected
✅ Reconciliation report generated and sent to Slack
```

### 🧾 Sample CSV Output
| tx_id | amount | status_internal | status_gateway | match_status |
|-------|---------|----------------|----------------|---------------|
| TXN001 | 15000 | success | success | ✅ |
| TXN002 | 12000 | failed | success | ❌ |
| TXN003 | 9000 | success | missing | ⚠️ |

---

## 📚 Project Structure

```
src/
├── main.py                 # Entry point
├── data_loader.py          # Load internal/gateway data
├── reconciler.py           # Compare and detect mismatches
├── notifier.py             # Slack notifications
├── config.py               # Environment and mappings
├── scheduler.py            # Periodic task runner
└── utils/
    ├── logger.py           # Logging utility
data/
├── internal_mock.csv
├── gateway_mock.csv
reports/
├── summary_2025-10-19.csv
```

---

## 🧰 Field Mappings

Mappings are defined dynamically in `config.py`:

```python
GATEWAY_MAPPINGS = {
    "paystack": {
        "reference": "tx_id",
        "amount": "amount",
        "status": "status",
        "currency": "currency",
        "paid_at": "created_at"
    },
    "stripe": {
        "id": "tx_id",
        "amount": "amount",
        "status": "status",
        "currency": "currency",
        "created": "created_at"
    }
}
```

---

## 🧑‍💻 Development Notes

- Built using **Python 3.10+**
- Logging powered by `logging` module
- Data pipelines via **Pandas**
- Compatible with **PostgreSQL**, **MySQL**, and **MongoDB**
- Slack integration via `slack_sdk`

---

## 🧠 Future Improvements

- Add webhook triggers for real-time reconciliation  
- Support for additional gateways (Flutterwave, PayPal)  
- Enhanced anomaly detection via ML  

---

## 💬 Support

If you run into issues:
- Open an issue on [GitHub Issues](https://github.com/your-username/transaction-reconciliation-bot/issues)
- Or message via Slack integration

---

## 🤝 Contributing

Contributions are welcome!  
1. Fork the repo  
2. Create a feature branch  
3. Commit changes and open a PR 🚀  

---

## 🪪 License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

---

## 🌐 Useful Links

- 🔗 [Slack API App Setup Guide](https://api.slack.com/apps)
- 💳 [Paystack API Docs](https://paystack.com/docs/api)
- 💰 [Stripe API Docs](https://stripe.com/docs/api)
- 🧾 [Pandas Documentation](https://pandas.pydata.org/docs/)
- ⚙️ [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- 🧠 [MongoDB PyMongo Docs](https://pymongo.readthedocs.io/)
