"""FastAPI application for spam detection service.

This API serves the trained spam detector model with the following endpoints:
- GET  /health          - Health check
- POST /predict         - Single message prediction
- POST /predict/batch   - Batch predictions
- GET  /metrics         - Model and system metrics
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List

import numpy as np
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .model_loader import get_model, get_metrics, get_model_info, is_model_loaded
from .schemas import (
    ErrorResponse,
    HealthResponse,
    MetricsResponse,
    PredictBatchRequest,
    PredictBatchResponse,
    PredictRequest,
    PredictResponse,
    PredictionResult,
)

# API version
API_VERSION = "1.0.0"

# Global metrics for monitoring
_api_metrics = {
    "start_time": time.time(),
    "total_predictions": 0,
    "total_requests": 0,
    "spam_detected": 0,
    "ham_detected": 0,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events - load model at startup."""
    # Startup: Don't load model yet for faster health checks
    print("=" * 80)
    print("🚀 Spam Detector API Starting...")
    print("=" * 80)
    print(f"✓ API version: {API_VERSION}")
    print("⏳ Loading model at startup...")
    print("=" * 80)

    try:
        get_model()
        print("✓ Model loaded at startup")
    except Exception as exc:
        print(f"✗ Model failed to load at startup: {exc}")

    yield

    # Shutdown: cleanup if needed
    print("\n👋 Shutting down Spam Detector API...")


# Create FastAPI app
app = FastAPI(
    title="Spam Detector API",
    description="ML-powered API for detecting spam in text messages and emails",
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    summary="Root endpoint",
    description="Returns basic API information",
)
async def root() -> Dict[str, str]:
    """Root endpoint with API information."""
    return {
        "name": "Spam Detector API",
        "version": API_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check if the API and model are healthy and ready",
)
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns:
        HealthResponse with status and model information

    Note:
        Always returns 'healthy' status for App Runner compatibility.
        Model is loaded lazily on first prediction request.
    """
    _api_metrics["total_requests"] += 1

    model_info = get_model_info()

    return HealthResponse(
        status="healthy",  # Always healthy - model loads on-demand
        model_loaded=model_info["loaded"],
        model_name=model_info.get("model_name"),
        version=API_VERSION,
    )


@app.post(
    "/predict",
    response_model=PredictResponse,
    summary="Predict single message",
    description="Classify a single message as spam or ham",
    responses={
        200: {"description": "Successful prediction"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def predict(request: PredictRequest) -> PredictResponse:
    """Predict whether a single message is spam or ham.

    Args:
        request: PredictRequest containing the message to classify

    Returns:
        PredictResponse with prediction and confidence

    Raises:
        HTTPException: If model is not loaded or prediction fails
    """
    _api_metrics["total_requests"] += 1

    # Check if model is loaded
    if not is_model_loaded():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model not loaded. Please check server logs.",
        )

    try:
        # Get model
        model = get_model()

        # Make prediction
        prediction = model.predict([request.message])[0]
        is_spam = bool(prediction == 1)

        # Get confidence if model supports predict_proba
        confidence = None
        if hasattr(model, "decision_function"):
            try:
                decision = model.decision_function([request.message])[0]
                # Convert decision function to probability-like score (0-1)
                confidence = float(1 / (1 + np.exp(-decision)))
            except Exception:
                pass

        # Update metrics
        _api_metrics["total_predictions"] += 1
        if is_spam:
            _api_metrics["spam_detected"] += 1
        else:
            _api_metrics["ham_detected"] += 1

        return PredictResponse(
            prediction="spam" if is_spam else "ham",
            is_spam=is_spam,
            confidence=confidence,
            message=request.message,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )


@app.post(
    "/predict/batch",
    response_model=PredictBatchResponse,
    summary="Predict batch of messages",
    description="Classify multiple messages at once",
    responses={
        200: {"description": "Successful predictions"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def predict_batch(request: PredictBatchRequest) -> PredictBatchResponse:
    """Predict whether multiple messages are spam or ham.

    Args:
        request: PredictBatchRequest containing messages to classify

    Returns:
        PredictBatchResponse with predictions for all messages

    Raises:
        HTTPException: If model is not loaded or prediction fails
    """
    _api_metrics["total_requests"] += 1

    # Check if model is loaded
    if not is_model_loaded():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model not loaded. Please check server logs.",
        )

    try:
        # Get model
        model = get_model()

        # Make predictions
        predictions = model.predict(request.messages)

        # Get confidences if available
        confidences = [None] * len(request.messages)
        if hasattr(model, "decision_function"):
            try:
                decisions = model.decision_function(request.messages)
                confidences = [
                    float(1 / (1 + np.exp(-d))) for d in decisions
                ]
            except Exception:
                pass

        # Build results
        results = []
        spam_count = 0
        ham_count = 0

        for i, (message, pred) in enumerate(zip(request.messages, predictions)):
            is_spam = bool(pred == 1)
            if is_spam:
                spam_count += 1
            else:
                ham_count += 1

            results.append(
                PredictionResult(
                    message=message,
                    prediction="spam" if is_spam else "ham",
                    is_spam=is_spam,
                    confidence=confidences[i],
                )
            )

        # Update metrics
        _api_metrics["total_predictions"] += len(request.messages)
        _api_metrics["spam_detected"] += spam_count
        _api_metrics["ham_detected"] += ham_count

        return PredictBatchResponse(
            predictions=results,
            total=len(results),
            spam_count=spam_count,
            ham_count=ham_count,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}",
        )


@app.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Get metrics",
    description="Get model performance metrics and API statistics",
)
async def get_api_metrics() -> MetricsResponse:
    """Get model and system metrics.

    Returns:
        MetricsResponse with ML metrics and API stats
    """
    _api_metrics["total_requests"] += 1

    # Get model metrics
    model_metrics = get_metrics()

    # Calculate system metrics
    uptime = time.time() - _api_metrics["start_time"]
    system_metrics = {
        "uptime_seconds": round(uptime, 2),
        "total_requests": _api_metrics["total_requests"],
        "total_predictions": _api_metrics["total_predictions"],
        "spam_detected": _api_metrics["spam_detected"],
        "ham_detected": _api_metrics["ham_detected"],
        "model_loaded": is_model_loaded(),
    }

    return MetricsResponse(
        model_metrics=model_metrics,
        system_metrics=system_metrics,
    )


# Error handlers
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
