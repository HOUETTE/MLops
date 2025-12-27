"""API module for serving the spam detector model."""

from .model_loader import get_model, load_model

__all__ = ["get_model", "load_model"]
