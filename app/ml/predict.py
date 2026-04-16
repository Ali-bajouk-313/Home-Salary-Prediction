import json
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts"

MODEL = joblib.load(ARTIFACTS / "model.joblib")
with open(ARTIFACTS / "feature_columns.json", "r") as f:
    METADATA = json.load(f)

FEATURE_MAP = {
    "overall_qual": "OverallQual",
    "gr_liv_area": "GrLivArea",
    "garage_cars": "GarageCars",
    "total_bsmt_sf": "TotalBsmtSF",
    "full_bath": "FullBath",
    "year_built": "YearBuilt",
    "neighborhood": "Neighborhood",
    "bedroom_abvgr": "BedroomAbvGr",
    "kitchen_qual": "KitchenQual",
    "lot_area": "LotArea",
    "fireplaces": "Fireplaces",
    "house_style": "HouseStyle",
}


def prepare_input(extracted_features: dict) -> pd.DataFrame:
    row = {model_key: extracted_features.get(api_key) for api_key, model_key in FEATURE_MAP.items()}
    return pd.DataFrame([row], columns=list(FEATURE_MAP.values()))


def predict_price(extracted_features: dict) -> float:
    df = prepare_input(extracted_features)
    prediction = MODEL.predict(df)[0]
    return float(prediction)