import os
import json
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from src.utils.logger import setup_logger

logger = setup_logger()

SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL_ID")
USE_SLACK = os.getenv("USE_SLACK", "False").lower() == "true"

client = WebClient(token=SLACK_TOKEN)


def send_slack_alert(summary, json_path):
    """
    Sends a structured Slack alert using Block Kit.
    Includes summary, discrepancies, and a Download Report button.
    """
    if not USE_SLACK:
        logger.info("ℹ️ Slack alerts disabled (USE_SLACK=False).")
        return

    if not SLACK_TOKEN:
        logger.warning("⚠️ SLACK_BOT_TOKEN not found. Skipping alert.")
        return

    if not SLACK_CHANNEL:
        logger.error("❌ SLACK_CHANNEL_ID not set. Message not sent.")
        return

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        discrepancies = [d for d in data if d.get("discrepancy_type") != "matched"]
        if not discrepancies:
            logger.info("✅ No discrepancies found. No Slack alert sent.")
            return

        # Upload full report first
        with open(json_path, "rb") as f:
            upload_response = client.files_upload_v2(
                channel=SLACK_CHANNEL,
                title=os.path.basename(json_path),
                initial_comment="📘 Full reconciliation report uploaded.",
                file=f
            )

        file_info = upload_response.get("file", {})
        file_url = file_info.get("url_private", None)

        # Build main summary
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"🧾 Fintech Reconciliation Report ({datetime.now().date()})"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*⚠️ Discrepancies detected:* {len(discrepancies)}"}
            },
            {"type": "divider"}
        ]

        # Add each discrepancy
        for item in discrepancies:
            tx_id = item.get("tx_id")
            disc = item.get("discrepancy_type")
            reason = item.get("probable_reason", "N/A")
            suggestion = item.get("suggested_action", "N/A")
            internal_status = item.get("status_internal", "N/A")
            gateway_status = item.get("status_gateway", "N/A")

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Transaction:* `{tx_id}`\n"
                        f"→ *Type:* {disc}\n"
                        f"→ *Internal:* `{internal_status}` | *Gateway:* `{gateway_status}`\n"
                        f"→ *Reason:* {reason}\n"
                        f"→ *Suggestion:* {suggestion}\n"
                    )
                }
            })
            blocks.append({"type": "divider"})

        # Add download button if available
        if file_url:
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "📥 Download Full Report"},
                        "url": file_url,
                        "style": "primary"
                    }
                ]
            })
        else:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": "📎 Full report saved locally in `reports/` folder."}
            })

        # Send message using Block Kit
        client.chat_postMessage(channel=SLACK_CHANNEL, blocks=blocks, text="Fintech Reconciliation Report")
        logger.info("✅ Slack summary with button sent successfully!")

    except SlackApiError as e:
        logger.error(f"❌ Slack API error: {e.response['error']}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
