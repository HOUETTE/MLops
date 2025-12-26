"""Model factory functions for the spam detector."""

from __future__ import annotations

from typing import Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from .config import MODEL_PARAMS, RANDOM_STATE, TFIDF_PARAMS
from .preprocessing import TextCleaner

AVAILABLE_MODELS = ("linear_svc", "multinomial_nb", "log_reg")


def _build_tfidf_vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(**TFIDF_PARAMS)


def _clean_step() -> TextCleaner:
    return TextCleaner()


def _linear_svc_pipeline() -> Pipeline:
    params: Dict = MODEL_PARAMS["linear_svc"]
    return Pipeline(
        [
            ("clean", _clean_step()),
            ("tfidf", _build_tfidf_vectorizer()),
            ("clf", LinearSVC(random_state=RANDOM_STATE, **params)),
        ]
    )


def _multinomial_nb_pipeline() -> Pipeline:
    params: Dict = MODEL_PARAMS["multinomial_nb"]
    return Pipeline(
        [
            ("clean", _clean_step()),
            ("tfidf", _build_tfidf_vectorizer()),
            ("clf", MultinomialNB(**params)),
        ]
    )


def _log_reg_pipeline() -> Pipeline:
    params: Dict = MODEL_PARAMS["log_reg"]
    return Pipeline(
        [
            ("clean", _clean_step()),
            ("tfidf", _build_tfidf_vectorizer()),
            (
                "clf",
                LogisticRegression(
                    random_state=RANDOM_STATE,
                    **params,
                ),
            ),
        ]
    )


def get_model_pipeline(model_name: str) -> Pipeline:
    """Return a pipeline matching the requested model."""
    normalized = model_name.lower()
    if normalized not in AVAILABLE_MODELS:
        raise ValueError(f"Unsupported model '{model_name}'. Choose from {AVAILABLE_MODELS}")

    if normalized == "linear_svc":
        return _linear_svc_pipeline()
    if normalized == "multinomial_nb":
        return _multinomial_nb_pipeline()
    return _log_reg_pipeline()
