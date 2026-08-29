from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier


RANDOM_SEED = 42

DATA_PATH = Path("ai_engine/data/training.csv")
MODEL_PATH = Path("ai_engine/models/xgboost_model.joblib")


def main():
    # Load dataset
    dataset = pd.read_csv(DATA_PATH)

    # Separate features and labels
    X = dataset.drop(columns=["label"])
    y = dataset["label"]

    # Convert class names to numeric labels
    label_names = sorted(y.unique())

    label_to_id = {
        label: index
        for index, label in enumerate(label_names)
    }

    y_encoded = y.map(label_to_id)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_encoded,
        test_size=0.2,
        random_state=RANDOM_SEED,
        stratify=y_encoded,
    )

    # Create XGBoost classifier
    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="multi:softprob",
        num_class=len(label_names),
        eval_metric="mlogloss",
        random_state=RANDOM_SEED,
    )

    # Train
    model.fit(X_train, y_train)

    # Predict
    predictions = model.predict(X_test)

    # Evaluate
    accuracy = accuracy_score(y_test, predictions)

    print("\nXGBoost Evaluation")
    print("==================")
    print(f"Accuracy: {accuracy:.4f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            target_names=label_names,
        )
    )

    # Save model + label mapping
    model_package = {
        "model": model,
        "label_names": label_names,
        "label_to_id": label_to_id,
        "feature_names": list(X.columns),
    }

    joblib.dump(model_package, MODEL_PATH)

    print(f"\nModel saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()