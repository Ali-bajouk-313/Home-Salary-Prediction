import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "train.csv"
ARTIFACTS = ROOT / "artifacts"
ARTIFACTS.mkdir(exist_ok=True)

TARGET = "SalePrice"

FEATURES = [
    "OverallQual",
    "GrLivArea",
    "GarageCars",
    "TotalBsmtSF",
    "FullBath",
    "YearBuilt",
    "Neighborhood",
    "BedroomAbvGr",
    "KitchenQual",
    "LotArea",
    "Fireplaces",
    "HouseStyle",
]


def build_preprocessor(df: pd.DataFrame):
    numeric_features = df[FEATURES].select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_features = [c for c in FEATURES if c not in numeric_features]

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    return ColumnTransformer([
        ("num", numeric_pipeline, numeric_features),
        ("cat", categorical_pipeline, categorical_features),
    ])


def evaluate_model(name, pipeline, x_train, x_val, y_train, y_val):
    pipeline.fit(x_train, y_train)
    preds = pipeline.predict(x_val)
    rmse = mean_squared_error(y_val, preds) ** 0.5
    r2 = r2_score(y_val, preds)
    return {"name": name, "model": pipeline, "rmse": rmse, "r2": r2}

def main():
    df = pd.read_csv(DATA_PATH)
    df = df[FEATURES + [TARGET]].dropna(subset=[TARGET])

    x = df[FEATURES]
    y = df[TARGET]

    x_train, x_temp, y_train, y_temp = train_test_split(
        x, y, test_size=0.3, random_state=42
    )
    x_val, x_test, y_val, y_test = train_test_split(
        x_temp, y_temp, test_size=0.5, random_state=42
    )

    preprocessor = build_preprocessor(df)

    candidates = [
        Pipeline([
            ("preprocessor", preprocessor),
            ("model", Ridge(alpha=1.0)),
        ]),
        Pipeline([
            ("preprocessor", preprocessor),
            ("model", RandomForestRegressor(
                n_estimators=200,
                max_depth=12,
                random_state=42,
                n_jobs=-1,
            )),
        ]),
    ]

    results = [
        evaluate_model("ridge", candidates[0], x_train, x_val, y_train, y_val),
        evaluate_model("random_forest", candidates[1], x_train, x_val, y_train, y_val),
    ]

    best = min(results, key=lambda r: r["rmse"])
    best_model = best["model"]

    test_preds = best_model.predict(x_test)
    test_rmse = mean_squared_error(y_test, test_preds) ** 0.5
    test_r2 = r2_score(y_test, test_preds)

    joblib.dump(best_model, ARTIFACTS / "model.joblib")

    metadata = {
        "features": FEATURES,
        "best_model": best["name"],
        "val_rmse": best["rmse"],
        "val_r2": best["r2"],
        "test_rmse": test_rmse,
        "test_r2": test_r2,
        "train_median_price": float(y_train.median()),
        "train_min_price": float(y_train.min()),
        "train_max_price": float(y_train.max()),
    }

    with open(ARTIFACTS / "feature_columns.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()