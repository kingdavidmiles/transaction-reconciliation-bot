import os
import pandas as pd
from openai import OpenAI
from src.config import *
from src.utils.logger import setup_logger
import os

logger = setup_logger()

# Initialize OpenAI client (modern SDK)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your_test_key_here"))


def rule_based_reason(row):
    """
    Simple deterministic logic for common mismatch scenarios.
    """
    mismatch = row.get("discrepancy_type", "")
    status_int = row.get("status_internal", "")
    status_gw = row.get("status_gateway", "")
    amt_int = row.get("amount_internal", 0)
    amt_gw = row.get("amount_gateway", 0)

    if mismatch == "missing_in_gateway":
        return (
            "Internal record exists but not found in gateway. "
            "Possible cause: failed API callback, unprocessed webhook, or gateway delay."
        )
    elif mismatch == "missing_in_internal":
        return (
            "Transaction found in gateway but missing internally. "
            "Possible cause: failed DB write, timeout after payment success, or system crash."
        )
    elif mismatch == "status_mismatch":
        return (
            f"Status differs (Internal: {status_int}, Gateway: {status_gw}). "
            "Likely due to delayed webhook update or manual override."
        )
    elif mismatch == "amount_mismatch":
        return (
            f"Amounts differ (Internal: {amt_int}, Gateway: {amt_gw}). "
            "Possible rounding error, currency conversion issue, or duplicate transaction."
        )
    elif mismatch == "currency_mismatch":
        return (
            "Currency inconsistency between systems. "
            "Likely config error or wrong payment channel mapping."
        )
    else:
        return "No issue detected."


def suggested_action(row):
    """
    Suggest developer or operations actions for quick resolution.
    """
    mismatch = row.get("discrepancy_type", "")
    if mismatch == "missing_in_gateway":
        return "Verify if gateway webhook/API callback was received; retry if necessary."
    elif mismatch == "missing_in_internal":
        return "Re-fetch transaction data from gateway and reinsert into DB."
    elif mismatch == "status_mismatch":
        return "Sync statuses by calling gateway verify endpoint."
    elif mismatch == "amount_mismatch":
        return "Escalate to finance for manual review."
    elif mismatch == "currency_mismatch":
        return "Check currency mapping and payment channel configuration."
    else:
        return "No action required."


def ai_explanation(row):
    """
    Use OpenAI (new API style) to generate natural-language explanations.
    """
    try:
        if row["discrepancy_type"] == "matched":
            return "Transaction is consistent across systems."

        prompt = (
            f"You are a fintech reconciliation assistant. Analyze the following discrepancy:\n\n"
            f"Transaction ID: {row['tx_id']}\n"
            f"Discrepancy Type: {row['discrepancy_type']}\n"
            f"Internal Data: amount={row.get('amount_internal')}, status={row.get('status_internal')}\n"
            f"Gateway Data: amount={row.get('amount_gateway')}, status={row.get('status_gateway')}\n\n"
            f"Explain clearly why this might have happened and what action should be taken."
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a fintech reconciliation expert."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.warning(f"AI explanation failed: {e}")
        return "AI explanation unavailable (check API key or rate limit)."



def enrich_with_analysis(df: pd.DataFrame):
    """
    Add rule-based and optional AI analysis to reconciliation results.
    Controlled by .env variable USE_AI=True/False
    """
    logger.info("Enriching report with analysis...")
    total = len(df)
    enriched_rows = []

    # Read AI toggle from environment
    use_ai = os.getenv("USE_AI", "False").lower() == "true"
    ai_limit = 5  # max AI calls to prevent quota issues

    if use_ai:
        logger.info("✅ AI analysis ENABLED (using OpenAI API).")
    else:
        logger.info("⚙️ AI analysis DISABLED (USE_AI=False). Skipping OpenAI calls.")

    for i, row in df.iterrows():
        tx_id = row.get('tx_id', 'N/A')
        logger.info(f"[{i+1}/{total}] Processing transaction {tx_id}...")

        # Rule-based logic
        row['probable_reason'] = rule_based_reason(row)
        row['suggested_action'] = suggested_action(row)

        # --- AI logic controlled by USE_AI ---
        if not use_ai:
            row['ai_explanation'] = "AI analysis skipped (USE_AI=False)."
        elif i >= ai_limit:
            row['ai_explanation'] = "Skipped AI analysis (limit reached)."
        else:
            try:
                row['ai_explanation'] = ai_explanation(row)
            except Exception as e:
                logger.warning(f"AI failed for {tx_id}: {e}")
                row['ai_explanation'] = "AI explanation unavailable due to quota or timeout."

        enriched_rows.append(row)

    enriched_df = pd.DataFrame(enriched_rows)
    logger.info(f"✅ Enrichment complete for {total} transactions.")
    return enriched_df
