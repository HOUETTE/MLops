"""Spam detector package."""

from .config import (
    DEFAULT_DATA_PATH,
    DEFAULT_MODELS_DIR,
    MODEL_PARAMS,
    RANDOM_STATE,
    TEST_SIZE,
    TFIDF_PARAMS,
)
from .data import load_dataset, train_test_split_data
from .evaluation import evaluate_model
from .modeling import AVAILABLE_MODELS, get_model_pipeline
from .preprocessing import clean_text

__all__ = [
    "DEFAULT_DATA_PATH",
    "DEFAULT_MODELS_DIR",
    "MODEL_PARAMS",
    "RANDOM_STATE",
    "TEST_SIZE",
    "TFIDF_PARAMS",
    "clean_text",
    "evaluate_model",
    "get_model_pipeline",
    "load_dataset",
    "train_test_split_data",
    "AVAILABLE_MODELS",
]
