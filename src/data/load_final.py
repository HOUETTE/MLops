"""Load final processed data for model training."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROCESSED_FILE = PROJECT_ROOT / "data" / "processed" / "spam_processed.csv"
DEFAULT_FINAL_FILE = PROJECT_ROOT / "data" / "spam.csv"


def load_final_data(
    input_path: Path | str = DEFAULT_PROCESSED_FILE,
    output_path: Path | str = DEFAULT_FINAL_FILE,
    save_to_s3: bool = False,
    s3_bucket: str | None = None,
    s3_key: str | None = None,
) -> pd.DataFrame:
    """Load final processed data and optionally upload to S3.

    This function:
    1. Loads the processed/cleaned data
    2. Performs final validation
    3. Saves to the final data location
    4. Optionally uploads to S3 for production use

    Args:
        input_path: Path to processed data
        output_path: Path to save final data locally
        save_to_s3: Whether to upload to S3
        s3_bucket: S3 bucket name (required if save_to_s3=True)
        s3_key: S3 object key (required if save_to_s3=True)

    Returns:
        Final DataFrame ready for model training
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    logger.info(f"Loading processed data from {input_path}")

    if not input_path.exists():
        raise FileNotFoundError(f"Processed data not found at {input_path}")

    # Load processed data
    df = pd.read_csv(input_path)
    logger.info(f"Loaded data shape: {df.shape}")

    # Final validation
    required_columns = {"Message", "Category"}
    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"Missing required columns. Expected {required_columns}, "
            f"got {set(df.columns)}"
        )

    # Ensure only necessary columns for training
    final_columns = ["Message", "Category"]
    df_final = df[final_columns].copy()

    # Log final statistics
    logger.info(f"Final dataset shape: {df_final.shape}")
    logger.info(f"Category distribution:\n{df_final['Category'].value_counts()}")

    # Save locally
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(output_path, index=False)
    logger.info(f"Saved final data to {output_path}")

    # Upload to S3 if requested
    if save_to_s3:
        if not s3_bucket or not s3_key:
            raise ValueError("s3_bucket and s3_key are required when save_to_s3=True")

        try:
            import boto3

            s3_client = boto3.client("s3")
            s3_client.upload_file(str(output_path), s3_bucket, s3_key)
            logger.info(f"✓ Uploaded to s3://{s3_bucket}/{s3_key}")
        except ImportError:
            logger.error("boto3 is required for S3 upload. Install with: pip install boto3")
            raise
        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}")
            raise

    return df_final


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Load final processed data for model training"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_PROCESSED_FILE,
        help="Input path for processed data",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_FINAL_FILE,
        help="Output path for final data",
    )
    parser.add_argument(
        "--s3-bucket",
        type=str,
        default=None,
        help="S3 bucket name for upload",
    )
    parser.add_argument(
        "--s3-key",
        type=str,
        default=None,
        help="S3 object key for upload",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for the load final script."""
    args = parse_args()

    try:
        df = load_final_data(
            input_path=args.input,
            output_path=args.output,
            save_to_s3=bool(args.s3_bucket and args.s3_key),
            s3_bucket=args.s3_bucket,
            s3_key=args.s3_key,
        )
        logger.info(f"✓ Successfully loaded final data: {len(df)} rows")
        sys.exit(0)
    except Exception as e:
        logger.error(f"✗ Failed to load final data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
