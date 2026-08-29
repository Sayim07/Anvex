from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest


DATA_PATH = Path("ai_engine/data/training.csv")
MODEL_PATH = Path("ai_engine/models/isolation_forest.joblib")


def main():
    dataset = pd.read_csv(DATA_PATH)

    # Learn the baseline from normal traffic only.
    normal_data = dataset[
        dataset["label"] == "normal"
    ].drop(columns=["label"])

    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42,
    )

    model.fit(normal_data)

    joblib.dump(
        {
            "model": model,
            "feature_names": list(normal_data.columns),
        },
        MODEL_PATH,
    )

    print("Isolation Forest trained.")
    print(f"Training samples: {len(normal_data)}")
    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()