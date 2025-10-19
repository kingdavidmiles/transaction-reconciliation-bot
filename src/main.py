from src.data_loader import load_internal_data, load_gateway_data
from src.recon_engine import reconcile
from src.utils.logger import setup_logger

logger = setup_logger()

def main():
    try:
        logger.info("=== Starting Fintech Reconciliation ===")
        df_internal = load_internal_data()
        df_gateway = load_gateway_data()

        result = reconcile(df_internal, df_gateway)

        summary = result['discrepancy_type'].value_counts().to_dict()
        total = len(result)
        mismatches = total - summary.get('matched', 0)

        print("\n=== FINTECH RECONCILIATION SUMMARY ===")
        print(f"✅ Total Checked: {total}")
        print(f"⚠️  Mismatches Found: {mismatches}")
        for key, val in summary.items():
            print(f" - {key}: {val}")
        print("\nReport saved in /reports/")
    except Exception as e:
        logger.error(f"Error during reconciliation: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
