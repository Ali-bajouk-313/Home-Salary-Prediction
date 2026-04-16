import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts"


def load_training_stats() -> dict:
    metadata_path = ARTIFACTS / "feature_columns.json"

    if not metadata_path.exists():
        return {
            "train_median_price": None,
            "train_min_price": None,
            "train_max_price": None,
            "best_model": None,
            "test_rmse": None,
            "test_r2": None,
        }

    with open(metadata_path, "r") as f:
        return json.load(f)


def _price_position(prediction: float, median_price: float) -> str:
    if median_price is None:
        return "around the typical range"

    ratio = prediction / median_price

    if ratio < 0.85:
        return "below the typical range"
    if ratio > 1.15:
        return "above the typical range"
    return "around the typical range"


def _feature_reasons(extracted) -> list[str]:
    reasons = []

    if extracted.gr_liv_area is not None:
        if extracted.gr_liv_area >= 2500:
            reasons.append("the larger living area pushes the estimate upward")
        elif extracted.gr_liv_area <= 1400:
            reasons.append("the smaller living area keeps the estimate more moderate")

    if extracted.overall_qual is not None:
        if extracted.overall_qual >= 8:
            reasons.append("the reported overall quality is a strong positive signal")
        elif extracted.overall_qual <= 5:
            reasons.append("the reported overall quality may limit the price")

    if extracted.garage_cars is not None and extracted.garage_cars >= 2:
        reasons.append("a multi-car garage adds practical value")

    if extracted.year_built is not None:
        if extracted.year_built >= 2000:
            reasons.append("the newer build year supports a stronger estimate")
        elif extracted.year_built <= 1970:
            reasons.append("the older build year may hold the price down unless renovated")

    if extracted.neighborhood:
        reasons.append(f"the neighborhood input ({extracted.neighborhood}) also influences the estimate")

    return reasons


def build_interpretation(extracted, prediction: float, confidence_score: float, confidence_label: str) -> str:

    stats = load_training_stats()

    median_price = stats.get("train_median_price")
    min_price = stats.get("train_min_price")
    max_price = stats.get("train_max_price")
    best_model = stats.get("best_model")
    test_rmse = stats.get("test_rmse")

    position = _price_position(prediction, median_price)
    reasons = _feature_reasons(extracted)

    intro = f"Estimated price: ${prediction:,.0f}."
    comparison = f"This appears {position}"
    if median_price is not None:
        comparison += f" compared with the training median of ${median_price:,.0f}."
    else:
        comparison += "."

    confidence_text = (
        f" Confidence is {confidence_label} ({confidence_score:.1f}%) "
        f"based on how many important property features were provided."
    )

    if reasons:
        details = " Key factors include " + "; ".join(reasons) + "."
    else:
        details = " The estimate is based on the extracted property features."

    range_text = ""
    if min_price is not None and max_price is not None:
        range_text = (
            f" In the training data, sale prices ranged from about "
            f"${min_price:,.0f} to ${max_price:,.0f}."
        )

    model_text = ""
    if best_model:
        model_text = f" The current prediction model is {best_model}."
        if test_rmse is not None:
            model_text += f" Its test RMSE is approximately {test_rmse:,.0f}."

    missing_text = ""
    if extracted.missing_features:
        missing_text = (
            f" Some optional features were not provided: "
            f"{', '.join(extracted.missing_features)}."
        )

    return intro + " " + comparison + confidence_text + details + range_text + model_text + missing_text

def calculate_confidence(extracted):
    critical_fields = [
        "gr_liv_area",
        "bedroom_abvgr",
        "full_bath",
        "year_built",
        "neighborhood",
    ]

    optional_fields = [
        "overall_qual",
        "garage_cars",
        "total_bsmt_sf",
        "kitchen_qual",
        "lot_area",
        "fireplaces",
        "house_style",
    ]

    critical_present = sum(
        1 for field in critical_fields
        if getattr(extracted, field) is not None
    )

    optional_present = sum(
        1 for field in optional_fields
        if getattr(extracted, field) is not None
    )

    critical_score = critical_present / len(critical_fields)
    optional_score = optional_present / len(optional_fields)

    score = round((0.7 * critical_score + 0.3 * optional_score) * 100, 1)

    if score >= 80:
        label = "high"
    elif score >= 50:
        label = "medium"
    else:
        label = "low"

    return score, label