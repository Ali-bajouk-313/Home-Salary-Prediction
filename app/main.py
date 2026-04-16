from fastapi import FastAPI

from app.schemas import (
    UserQuery,
    PredictionResponse,
    StructuredPredictionRequest,
    ExtractedFeatures,
)
from app.ml.predict import predict_price
from app.llm.extractor import extract_features_from_query, refresh_metadata
from app.llm.interpreter import build_interpretation, load_training_stats
from app.utils.confidence import calculate_confidence

app = FastAPI(title="AI Real Estate Agent")

FEATURE_FIELDS = [
    "overall_qual",
    "gr_liv_area",
    "garage_cars",
    "total_bsmt_sf",
    "full_bath",
    "year_built",
    "neighborhood",
    "bedroom_abvgr",
    "kitchen_qual",
    "lot_area",
    "fireplaces",
    "house_style",
]

CRITICAL_FIELDS = [
    "gr_liv_area",
    "bedroom_abvgr",
    "full_bath",
    "year_built",
    "neighborhood",
]


def refresh_feature_lists(extracted: ExtractedFeatures) -> ExtractedFeatures:
    return refresh_metadata(extracted.model_dump())


def build_response_from_features(extracted: ExtractedFeatures) -> PredictionResponse:
    extracted = refresh_feature_lists(extracted)
    stats = load_training_stats()

    missing_critical = [
        field for field in CRITICAL_FIELDS
        if getattr(extracted, field) is None
    ]

    confidence_score, confidence_label = calculate_confidence(extracted)

    if len(extracted.provided_features) == 0:
        return PredictionResponse(
            extracted_features=extracted,
            prediction=None,
            interpretation=(
                "I could not extract any pricing details from your description. "
                "Please provide at least the living area, number of bedrooms, "
                "number of bathrooms, year built, and neighborhood."
            ),
            missing_fields_needed=CRITICAL_FIELDS,
            confidence_score=0.0,
            confidence_label="low",
            status="needs_more_info",
            training_stats={
                "train_median_price": stats.get("train_median_price"),
                "train_min_price": stats.get("train_min_price"),
                "train_max_price": stats.get("train_max_price"),
            },
        )

    prediction = predict_price(extracted.model_dump())
    interpretation = build_interpretation(
        extracted,
        prediction,
        confidence_score,
        confidence_label,
        missing_critical,
    )

    if missing_critical:
        return PredictionResponse(
            extracted_features=extracted,
            prediction=prediction,
            interpretation=interpretation,
            missing_fields_needed=missing_critical,
            confidence_score=confidence_score,
            confidence_label=confidence_label,
            status="partial_success",
            training_stats={
                "train_median_price": stats.get("train_median_price"),
                "train_min_price": stats.get("train_min_price"),
                "train_max_price": stats.get("train_max_price"),
            },
        )

    return PredictionResponse(
        extracted_features=extracted,
        prediction=prediction,
        interpretation=interpretation,
        missing_fields_needed=[],
        confidence_score=confidence_score,
        confidence_label=confidence_label,
        status="success",
        training_stats={
            "train_median_price": stats.get("train_median_price"),
            "train_min_price": stats.get("train_min_price"),
            "train_max_price": stats.get("train_max_price"),
        },
    )


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: UserQuery):
    try:
        extracted = extract_features_from_query(payload.query)
        return build_response_from_features(extracted)
    except Exception as e:
        try:
            extracted = extract_features_from_query(payload.query)
        except Exception:
            extracted = ExtractedFeatures(
                provided_features=[],
                missing_features=FEATURE_FIELDS,
                confident_features=[],
            )

        return PredictionResponse(
            extracted_features=extracted,
            prediction=None,
            interpretation=f"Prediction failed: {str(e)}",
            missing_fields_needed=[],
            confidence_score=0.0,
            confidence_label="low",
            status="error",
            training_stats={},
        )


@app.post("/predict_from_features", response_model=PredictionResponse)
def predict_from_features(payload: StructuredPredictionRequest):
    try:
        return build_response_from_features(payload.features)
    except Exception as e:
        extracted = refresh_feature_lists(payload.features)

        return PredictionResponse(
            extracted_features=extracted,
            prediction=None,
            interpretation=f"Prediction failed: {str(e)}",
            missing_fields_needed=[],
            confidence_score=0.0,
            confidence_label="low",
            status="error",
            training_stats={},
        )