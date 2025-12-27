"""Download spam dataset from various sources."""

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
DEFAULT_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DEFAULT_OUTPUT_FILE = DEFAULT_RAW_DIR / "spam_raw.csv"


def download_spam_dataset(
    output_path: Path | str = DEFAULT_OUTPUT_FILE,
    source: str = "local",
) -> Path:
    """Download spam dataset from specified source.

    Args:
        output_path: Where to save the downloaded data
        source: Data source ('local', 's3', 'url')

    Returns:
        Path to the downloaded file

    Note:
        This is a placeholder implementation. In production, you would:
        - Download from Kaggle API
        - Pull from S3 bucket
        - Fetch from public URL
        - Query from database (RDS, Aurora)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Downloading spam dataset from source: {source}")

    if source == "local":
        # Check if we already have the data in data/spam.csv
        existing_data = PROJECT_ROOT / "data" / "spam.csv"
        if existing_data.exists():
            logger.info(f"Found existing data at {existing_data}")
            # Copy to raw directory
            df = pd.read_csv(existing_data)
            df.to_csv(output_path, index=False)
            logger.info(f"Copied data to {output_path}")
            logger.info(f"Dataset shape: {df.shape}")
            return output_path
        else:
            raise FileNotFoundError(
                f"No local data found at {existing_data}. "
                "Please provide a spam dataset or use a different source."
            )

    elif source == "s3":
        # TODO: Implement S3 download using boto3
        # Example:
        # import boto3
        # s3 = boto3.client('s3')
        # s3.download_file('your-bucket', 'spam.csv', str(output_path))
        raise NotImplementedError("S3 download not yet implemented")

    elif source == "url":
        # TODO: Implement URL download
        # Example: download from public dataset repository
        raise NotImplementedError("URL download not yet implemented")

    else:
        raise ValueError(f"Unknown source: {source}")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Download spam dataset from various sources"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_FILE,
        help="Output path for downloaded data",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="local",
        choices=["local", "s3", "url"],
        help="Data source",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for the download script."""
    args = parse_args()

    try:
        output_file = download_spam_dataset(
            output_path=args.output,
            source=args.source,
        )
        logger.info(f"✓ Successfully downloaded data to {output_file}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"✗ Failed to download data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
