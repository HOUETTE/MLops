"""Model loader for the spam detector API.

This module handles loading and caching the trained ML model.
The model is loaded once at startup and reused for all predictions.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import joblib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "linear_svc.joblib"
DEFAULT_METRICS_PATH = PROJECT_ROOT / "models" / "linear_svc_metrics.json"

# Global model cache (singleton pattern)
_model_cache: Optional[Any] = None
_metrics_cache: Optional[Dict] = None


def load_model(model_path: Path | str = DEFAULT_MODEL_PATH) -> Any:
    """Load a trained model from disk.

    Args:
        model_path: Path to the .joblib model file

    Returns:
        Loaded scikit-learn pipeline

    Raises:
        FileNotFoundError: If model file doesn't exist
        Exception: If model loading fails
    """
    model_path = Path(model_path)

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found at {model_path}. "
            f"Please train a model first using: python training/train.py"
        )

    try:
        logger.info(f"Loading model from {model_path}")
        model = joblib.load(model_path)
        logger.info("✓ Model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"✗ Failed to load model: {e}")
        raise


def load_metrics(metrics_path: Path | str = DEFAULT_METRICS_PATH) -> Dict:
    """Load model metrics from JSON file.

    Args:
        metrics_path: Path to the metrics JSON file

    Returns:
        Dictionary containing model performance metrics
    """
    metrics_path = Path(metrics_path)

    if not metrics_path.exists():
        logger.warning(f"Metrics file not found at {metrics_path}")
        return {}

    try:
        with metrics_path.open("r") as f:
            metrics = json.load(f)
        logger.info("✓ Metrics loaded successfully")
        return metrics
    except Exception as e:
        logger.error(f"✗ Failed to load metrics: {e}")
        return {}


def get_model(
    model_path: Path | str = DEFAULT_MODEL_PATH,
    force_reload: bool = False,
) -> Any:
    """Get the model instance (cached singleton).

    This function loads the model once and caches it for subsequent calls.
    This avoids reloading the model for every API request.

    Args:
        model_path: Path to the model file
        force_reload: If True, reload the model even if cached

    Returns:
        Cached or freshly loaded model instance
    """
    global _model_cache

    if _model_cache is None or force_reload:
        logger.info("Loading model into cache...")
        _model_cache = load_model(model_path)
    else:
        logger.debug("Using cached model")

    return _model_cache


def get_metrics(
    metrics_path: Path | str = DEFAULT_METRICS_PATH,
    force_reload: bool = False,
) -> Dict:
    """Get the model metrics (cached singleton).

    Args:
        metrics_path: Path to the metrics file
        force_reload: If True, reload metrics even if cached

    Returns:
        Cached or freshly loaded metrics dictionary
    """
    global _metrics_cache

    if _metrics_cache is None or force_reload:
        logger.info("Loading metrics into cache...")
        _metrics_cache = load_metrics(metrics_path)
    else:
        logger.debug("Using cached metrics")

    return _metrics_cache


def is_model_loaded() -> bool:
    """Check if a model is currently loaded in cache.

    Returns:
        True if model is loaded, False otherwise
    """
    return _model_cache is not None


def get_model_info() -> Dict[str, Any]:
    """Get information about the loaded model.

    Returns:
        Dictionary with model status and metadata
    """
    if not is_model_loaded():
        return {
            "loaded": False,
            "model_path": str(DEFAULT_MODEL_PATH),
            "message": "Model not loaded yet",
        }

    metrics = get_metrics()

    return {
        "loaded": True,
        "model_path": str(DEFAULT_MODEL_PATH),
        "model_name": metrics.get("model", "unknown"),
        "accuracy": metrics.get("accuracy"),
        "precision": metrics.get("precision"),
        "recall": metrics.get("recall"),
        "f1_score": metrics.get("f1"),
        "roc_auc": metrics.get("roc_auc"),
    }
