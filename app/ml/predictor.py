import joblib
import pandas as pd

from app.config import settings
from app.exceptions import ModelPredictionError


model_package = joblib.load(settings.model_path)

if isinstance(model_package, dict):
    if "model" not in model_package:
        raise KeyError(
            f"Expected key 'model' in saved model package. "
            f"Found keys: {list(model_package.keys())}"
        )

    model = model_package["model"]

    FRAUD_THRESHOLD = model_package.get(
        "threshold",
        settings.default_fraud_threshold,
    )

    MODEL_VERSION = model_package.get(
        "model_version",
        settings.default_model_version,
    )

    SKLEARN_VERSION = model_package.get(
        "sklearn_version",
        "unknown",
    )

    FEATURES = model_package.get(
        "features",
        [],
    )
else:
    model = model_package
    FRAUD_THRESHOLD = settings.default_fraud_threshold
    MODEL_VERSION = settings.default_model_version
    SKLEARN_VERSION = "unknown"
    FEATURES = []


def get_risk_level(fraud_probability: float) -> str:
    if fraud_probability >= 0.8:
        return "high"

    if fraud_probability >= 0.5:
        return "medium"

    if fraud_probability >= 0.2:
        return "low"

    return "very_low"


def predict_transaction(transaction_data: dict) -> dict:
    try:
        input_df = pd.DataFrame([transaction_data])

        fraud_probability = float(
            model.predict_proba(input_df)[0][1]
        )

    except Exception as exc:
        raise ModelPredictionError("Model prediction failed") from exc

    if fraud_probability >= FRAUD_THRESHOLD:
        prediction = "fraud"
    else:
        prediction = "not_fraud"

    return {
        "prediction": prediction,
        "risk_level": get_risk_level(fraud_probability),
        "fraud_probability": round(fraud_probability, 6),
        "threshold_used": FRAUD_THRESHOLD,
        "model_version": MODEL_VERSION,
    }


def get_model_info() -> dict:
    return {
        "model_version": MODEL_VERSION,
        "sklearn_version": SKLEARN_VERSION,
        "threshold_used": FRAUD_THRESHOLD,
        "model_type": type(model).__name__,
        "features": FEATURES,
    }