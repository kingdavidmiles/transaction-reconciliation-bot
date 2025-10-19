from dotenv import load_dotenv
load_dotenv()

import os
import json
import pandas as pd
from datetime import datetime
from colorama import Fore, Style
from src.utils.logger import setup_logger
from src.config import REPORT_PATH
from src.analyzer import enrich_with_analysis
from src.notifier.slack_notifier import send_slack_alert  # ✅ use the real notifier

logger = setup_logger()

# Read environment variables
USE_SLACK = os.getenv("USE_SLACK", "False").lower() in ["true", "1", "yes"]


def normalize(df: pd.DataFrame, source_name: str):
    """
    Normalize column names and types.
    """
    df = df.rename(columns=str.lower)
    if 'reference' in df.columns:
        df.rename(columns={'reference': 'tx_id'}, inplace=True)
    if 'id' in df.columns:
        df.rename(columns={'id': 'tx_id'}, inplace=True)

    df['source'] = source_name
    df['tx_id'] = df['tx_id'].astype(str)
    if 'amount' in df.columns:
        df['amount'] = df['amount'].astype(float)
    if 'status' in df.columns:
        df['status'] = df['status'].str.lower()

    return df


def reconcile(df_internal: pd.DataFrame, df_gateway: pd.DataFrame):
    """
    Compare internal and gateway data and classify discrepancies.
    """
    logger.info("Starting reconciliation...")

    df_internal = normalize(df_internal, 'internal')
    df_gateway = normalize(df_gateway, 'gateway')

    merged = pd.merge(
        df_internal,
        df_gateway,
        on='tx_id',
        how='outer',
        suffixes=('_internal', '_gateway'),
        indicator=True
    )

    def classify(row):
        if row['_merge'] == 'left_only':
            return 'missing_in_gateway'
        elif row['_merge'] == 'right_only':
            return 'missing_in_internal'
        else:
            if row['amount_internal'] != row['amount_gateway']:
                return 'amount_mismatch'
            elif row['status_internal'] != row['status_gateway']:
                return 'status_mismatch'
            elif row.get('currency_internal') != row.get('currency_gateway'):
                return 'currency_mismatch'
            else:
                return 'matched'

    merged['discrepancy_type'] = merged.apply(classify, axis=1)
    result = merged.drop(columns=['_merge'])

    # Save report (CSV + JSON)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    save_report(result, timestamp)

    # Send Slack alert if there are discrepancies
    discrepancies = result[result['discrepancy_type'] != 'matched']
    if not discrepancies.empty and USE_SLACK:
        summary = (
            f"🧾 *Fintech Reconciliation Report ({datetime.now().date()})*\n"
            f"⚠️ Discrepancies detected: {len(discrepancies)}\n\n"
        )

        for _, row in discrepancies.iterrows():
            summary += (
                f"• `{row['tx_id']}` → *{row['discrepancy_type']}*\n"
                f"   ├ Reason: {row.get('probable_reason', 'N/A')}\n"
                f"   ├ Suggestion: {row.get('suggested_action', 'N/A')}\n"
                f"   └ Status → Internal: {row.get('status_internal', 'N/A')} | "
                f"Gateway: {row.get('status_gateway', 'N/A')}\n\n"
            )

        json_path = os.path.join("reports", f"reconciliation_report_{timestamp}.json")
        summary += f"📎 Full report saved as `{json_path}`"

        send_slack_alert(summary, json_path)
    else:
        logger.info("✅ No discrepancies found or Slack disabled — no alert sent.")

    return result


def save_report(df: pd.DataFrame, timestamp: str):
    """
    Enrich and save reconciliation results to CSV + JSON.
    Includes timestamped filenames for tracking.
    """
    os.makedirs("reports", exist_ok=True)

    # Build filenames
    csv_filename = f"reconciliation_report_{timestamp}.csv"
    json_filename = f"reconciliation_report_{timestamp}.json"

    csv_path = os.path.join("reports", csv_filename)
    json_path = os.path.join("reports", json_filename)

    # Enrich data
    df = enrich_with_analysis(df)

    # Save CSV
    df.to_csv(csv_path, index=False)
    logger.info(f"✅ CSV report saved to {csv_path}")

    # Save JSON (convert NaN -> null)
    data = json.loads(df.to_json(orient="records", indent=4))
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    logger.info(f"✅ JSON report saved to {json_path}")

    # Print colorized summary in terminal
    print(Fore.CYAN + "\n=== RECONCILIATION SUMMARY ===" + Style.RESET_ALL)
    for record in data:
        print(Fore.YELLOW + f"\nTransaction ID: {record.get('tx_id')}" + Style.RESET_ALL)
        print(Fore.GREEN + f"  Internal Status: {record.get('status_internal')}" + Style.RESET_ALL)
        print(Fore.GREEN + f"  Gateway Status:  {record.get('status_gateway')}" + Style.RESET_ALL)
        print(Fore.MAGENTA + f"  Discrepancy: {record.get('discrepancy_type')}" + Style.RESET_ALL)
        print(Fore.BLUE + f"  Reason: {record.get('probable_reason')}" + Style.RESET_ALL)
        print(Fore.CYAN + f"  Action: {record.get('suggested_action')}" + Style.RESET_ALL)
        print(Fore.LIGHTBLACK_EX + f"  AI Note: {record.get('ai_explanation')}" + Style.RESET_ALL)
        print(Fore.WHITE + "-" * 90 + Style.RESET_ALL)

    print(Fore.GREEN + "\n✅ Report generation complete.\n" + Style.RESET_ALL)
