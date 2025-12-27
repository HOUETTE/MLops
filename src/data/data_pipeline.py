"""Main data pipeline orchestration script.

This script orchestrates the complete ETL pipeline:
1. Download raw data
2. Clean and transform
3. Load final data (with optional S3 upload)
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Import ETL functions
from download_data import download_spam_dataset
from clean_transform import clean_and_transform
from load_final import load_final_data


def run_data_pipeline(
    source: str = "local",
    upload_to_s3: bool = False,
    s3_bucket: str | None = None,
    s3_key: str | None = None,
) -> dict:
    """Run the complete data pipeline.

    Args:
        source: Data source ('local', 's3', 'url')
        upload_to_s3: Whether to upload final data to S3
        s3_bucket: S3 bucket name
        s3_key: S3 object key

    Returns:
        Dictionary with pipeline execution statistics
    """
    start_time = time.time()
    stats = {
        "success": False,
        "steps_completed": [],
        "errors": [],
    }

    try:
        # Step 1: Download data
        logger.info("=" * 80)
        logger.info("STEP 1/3: Downloading data")
        logger.info("=" * 80)
        raw_file = PROJECT_ROOT / "data" / "raw" / "spam_raw.csv"
        download_spam_dataset(output_path=raw_file, source=source)
        stats["steps_completed"].append("download")
        stats["raw_file"] = str(raw_file)

        # Step 2: Clean and transform
        logger.info("\n" + "=" * 80)
        logger.info("STEP 2/3: Cleaning and transforming data")
        logger.info("=" * 80)
        processed_file = PROJECT_ROOT / "data" / "processed" / "spam_processed.csv"
        df_cleaned = clean_and_transform(
            input_path=raw_file,
            output_path=processed_file,
        )
        stats["steps_completed"].append("clean_transform")
        stats["processed_file"] = str(processed_file)
        stats["rows_processed"] = len(df_cleaned)

        # Step 3: Load final data
        logger.info("\n" + "=" * 80)
        logger.info("STEP 3/3: Loading final data")
        logger.info("=" * 80)
        final_file = PROJECT_ROOT / "data" / "spam.csv"
        df_final = load_final_data(
            input_path=processed_file,
            output_path=final_file,
            save_to_s3=upload_to_s3,
            s3_bucket=s3_bucket,
            s3_key=s3_key,
        )
        stats["steps_completed"].append("load_final")
        stats["final_file"] = str(final_file)
        stats["final_rows"] = len(df_final)

        # Success!
        stats["success"] = True
        elapsed_time = time.time() - start_time
        stats["elapsed_seconds"] = round(elapsed_time, 2)

        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"✓ Steps completed: {', '.join(stats['steps_completed'])}")
        logger.info(f"✓ Final dataset: {stats['final_rows']} rows")
        logger.info(f"✓ Output file: {stats['final_file']}")
        logger.info(f"✓ Elapsed time: {stats['elapsed_seconds']}s")
        if upload_to_s3:
            logger.info(f"✓ Uploaded to S3: s3://{s3_bucket}/{s3_key}")
        logger.info("=" * 80)

        return stats

    except Exception as e:
        logger.error(f"\n✗ Pipeline failed at step {len(stats['steps_completed']) + 1}")
        logger.error(f"✗ Error: {e}")
        stats["errors"].append(str(e))
        elapsed_time = time.time() - start_time
        stats["elapsed_seconds"] = round(elapsed_time, 2)
        raise


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the complete data pipeline (ETL)"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="local",
        choices=["local", "s3", "url"],
        help="Data source",
    )
    parser.add_argument(
        "--upload-to-s3",
        action="store_true",
        help="Upload final data to S3",
    )
    parser.add_argument(
        "--s3-bucket",
        type=str,
        default=None,
        help="S3 bucket name",
    )
    parser.add_argument(
        "--s3-key",
        type=str,
        default="data/spam.csv",
        help="S3 object key",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for the data pipeline."""
    args = parse_args()

    try:
        stats = run_data_pipeline(
            source=args.source,
            upload_to_s3=args.upload_to_s3,
            s3_bucket=args.s3_bucket,
            s3_key=args.s3_key,
        )

        if stats["success"]:
            logger.info("\n✓ Data pipeline completed successfully!")
            sys.exit(0)
        else:
            logger.error("\n✗ Data pipeline failed!")
            sys.exit(1)

    except Exception as e:
        logger.error(f"\n✗ Pipeline execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
