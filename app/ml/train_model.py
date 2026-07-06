import joblib
import pandas as pd
import sklearn

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DATA_PATH = "data/fraud.csv"
MODEL_PATH = "app/ml/fraud_model.pkl"

MODEL_VERSION = "v1.0"
SAMPLE_SIZE = 1_000_000

FEATURES = [
    "type",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
]

TARGET = "isFraud"


def load_data():
    df = pd.read_csv(DATA_PATH)

    if SAMPLE_SIZE is not None and SAMPLE_SIZE < len(df):
        df = df.sample(
            SAMPLE_SIZE,
            random_state=42,
        )

    X = df[FEATURES]
    y = df[TARGET]

    return X, y


def build_pipeline():
    categorical_features = ["type"]

    numeric_features = [
        "amount",
        "oldbalanceOrg",
        "newbalanceOrig",
        "oldbalanceDest",
        "newbalanceDest",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features,
            ),
            (
                "num",
                StandardScaler(),
                numeric_features,
            ),
        ]
    )

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    return pipeline


def train():
    X, y = load_data()

    print("Dataset loaded successfully.")
    print(f"Total samples: {len(X)}")

    print("\nClass distribution:")
    print(y.value_counts())

    X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42,
    stratify=y,
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.5,
        random_state=42,
        stratify=y_temp,
    )

    print("\nDataset Split:")
    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    print(f"Test samples: {len(X_test)}")

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_val_prob = pipeline.predict_proba(X_val)[:, 1]

    thresholds = [
        0.2,
        0.3,
        0.4,
        0.5,
        0.6,
        0.7,
        0.8,
    ]

    print("\nThreshold Analysis:")

    best_threshold = 0.5
    best_f1 = 0.0

    for threshold in thresholds:
        y_pred_threshold = (y_val_prob >= threshold).astype(int)

        precision = precision_score(
            y_val,
            y_pred_threshold,
            zero_division=0,
        )

        recall = recall_score(
            y_val,
            y_pred_threshold,
            zero_division=0,
        )

        f1 = f1_score(
            y_val,
            y_pred_threshold,
            zero_division=0,
        )

        print(
            f"Threshold: {threshold} | "
            f"Precision: {precision:.4f} | "
            f"Recall: {recall:.4f} | "
            f"F1: {f1:.4f}"
        )

        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold

        
    print(f"\nBest threshold based on F1: {best_threshold}")

    y_test_prob = pipeline.predict_proba(X_test)[:, 1]

    y_pred_final = (y_test_prob >= best_threshold).astype(int)

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred_final))

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred_final))

    print("\nROC-AUC Score:")
    print(roc_auc_score(y_test, y_test_prob))

    print("\nPR-AUC Score:")
    print(average_precision_score(y_test, y_test_prob))

    model_package = {
        "model": pipeline,
        "threshold": best_threshold,
        "model_version": MODEL_VERSION,
        "sklearn_version": sklearn.__version__,
        "features": FEATURES,
    }

    joblib.dump(
        model_package,
        MODEL_PATH,
    )

    print(f"\nModel saved to {MODEL_PATH}")
    print(f"Model version: {MODEL_VERSION}")
    print(f"scikit-learn version: {sklearn.__version__}")


if __name__ == "__main__":
    train()