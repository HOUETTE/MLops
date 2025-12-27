"""Pydantic schemas for request/response validation."""

from typing import List, Optional

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """Request schema for single message prediction."""

    message: str = Field(
        ...,
        description="Email or text message to classify",
        min_length=1,
        examples=["Get rich quick! Click here now!"],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Congratulations! You've won a free iPhone. Click here to claim."
            }
        }


class PredictBatchRequest(BaseModel):
    """Request schema for batch predictions."""

    messages: List[str] = Field(
        ...,
        description="List of messages to classify",
        min_length=1,
        max_length=100,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    "Meeting at 3pm tomorrow",
                    "WIN FREE MONEY NOW!!!",
                    "Can you send me the report?",
                ]
            }
        }


class PredictionResult(BaseModel):
    """Schema for a single prediction result."""

    message: str = Field(..., description="Original message")
    prediction: str = Field(..., description="Predicted class: 'spam' or 'ham'")
    is_spam: bool = Field(..., description="True if spam, False if ham")
    confidence: Optional[float] = Field(
        None, description="Confidence score (if available)"
    )


class PredictResponse(BaseModel):
    """Response schema for single prediction."""

    prediction: str = Field(..., description="Predicted class: 'spam' or 'ham'")
    is_spam: bool = Field(..., description="True if spam, False if ham")
    confidence: Optional[float] = Field(None, description="Confidence score")
    message: str = Field(..., description="Original message")

    class Config:
        json_schema_extra = {
            "example": {
                "prediction": "spam",
                "is_spam": True,
                "confidence": 0.98,
                "message": "WIN FREE MONEY NOW!!!",
            }
        }


class PredictBatchResponse(BaseModel):
    """Response schema for batch predictions."""

    predictions: List[PredictionResult]
    total: int = Field(..., description="Total number of predictions")
    spam_count: int = Field(..., description="Number of spam messages")
    ham_count: int = Field(..., description="Number of ham messages")

    class Config:
        json_schema_extra = {
            "example": {
                "predictions": [
                    {
                        "message": "Meeting at 3pm",
                        "prediction": "ham",
                        "is_spam": False,
                        "confidence": 0.95,
                    },
                    {
                        "message": "WIN FREE MONEY!!!",
                        "prediction": "spam",
                        "is_spam": True,
                        "confidence": 0.99,
                    },
                ],
                "total": 2,
                "spam_count": 1,
                "ham_count": 1,
            }
        }


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""

    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    model_name: Optional[str] = Field(None, description="Name of loaded model")
    version: str = Field(..., description="API version")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "model_loaded": True,
                "model_name": "linear_svc",
                "version": "1.0.0",
            }
        }


class MetricsResponse(BaseModel):
    """Response schema for metrics endpoint."""

    model_metrics: dict = Field(..., description="ML model performance metrics")
    system_metrics: dict = Field(..., description="System/API metrics")

    class Config:
        json_schema_extra = {
            "example": {
                "model_metrics": {
                    "model": "linear_svc",
                    "accuracy": 0.9956,
                    "precision": 0.9963,
                    "recall": 0.9854,
                    "f1": 0.9908,
                    "roc_auc": 0.9999,
                },
                "system_metrics": {
                    "uptime_seconds": 3600,
                    "total_predictions": 150,
                    "cache_size": 1,
                },
            }
        }


class ErrorResponse(BaseModel):
    """Response schema for errors."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Model not loaded",
                "detail": "Please ensure the model file exists at models/linear_svc.joblib",
            }
        }
