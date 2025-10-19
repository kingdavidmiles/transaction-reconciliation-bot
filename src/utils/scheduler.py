import schedule
import time
import pandas as pd
from datetime import datetime
from src.recon_engine import reconcile
from src.notifier.slack_notifier import send_slack_report

def run_reconciliation():
    print("🔄 Running reconciliation task...")
    try:
        # Load data
        df_internal = pd.read_csv("data/internal.csv")
        df_gateway = pd.read_csv("data/gateway.csv")

        result = reconcile(df_internal, df_gateway)

        mismatches = result[result["discrepancy_type"] != "matched"]
        date_str = datetime.now().strftime("%Y-%m-%d")
        csv_file = f"reports/reconciliation_report_{date_str}.csv"

        if not mismatches.empty:
            message = (
                f"⚠️ Reconciliation Report - Discrepancies Found ({date_str})\n"
                f"{len(mismatches)} transactions have mismatches. "
                f"CSV report attached."
            )
            send_slack_report(message, file_path=csv_file)
        else:
            print("✅ All transactions matched. No Slack notification sent.")

    except Exception as e:
        error_message = f"❌ Reconciliation Job Failed on {date_str}\nError: {e}"
        send_slack_report(error_message)
        print(f"❌ Error during reconciliation: {e}")

# Schedule job for midnight
schedule.every().day.at("00:00").do(run_reconciliation)

print("🕛 Scheduler running... (waiting for midnight trigger)")
while True:
    schedule.run_pending()
    time.sleep(60)
