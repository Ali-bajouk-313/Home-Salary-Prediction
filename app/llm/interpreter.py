import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts"
MODEL_NAME = "gemini-1.5-flash"

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


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


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"([.,!?])([A-Za-z])", r"\1 \2", text)
    return text


def build_home_summary(extracted) -> str:
    parts = []

    if extracted.bedroom_abvgr is not None:
        parts.append(f"{extracted.bedroom_abvgr}-bedroom")

    if extracted.full_bath is not None:
        parts.append(f"{extracted.full_bath}-bathroom")

    home_type = "home"
    summary = " ".join(parts).strip()
    if summary:
        summary += f" {home_type}"
    else:
        summary = home_type

    details = []

    if extracted.gr_liv_area is not None:
        details.append(f"with about {extracted.gr_liv_area:,.0f} sqft of living space")

    if extracted.garage_cars is not None:
        details.append(f"a {extracted.garage_cars:,.0f}-car garage")

    if extracted.year_built is not None:
        details.append(f"built in {extracted.year_built}")

    if extracted.neighborhood:
        details.append(f"located in {extracted.neighborhood}")

    if details:
        summary += " " + ", ".join(details)

    return summary


def build_fallback_interpretation(
    extracted,
    prediction: float,
    confidence_score: float,
    confidence_label: str,
    missing_critical: list[str],
) -> str:
    stats = load_training_stats()
    median_price = stats.get("train_median_price")

    home_summary = build_home_summary(extracted)
    parts = [
        f"This property appears to be a {home_summary}.",
        f"The estimated value is about ${prediction:,.0f}.",
    ]

    if median_price is not None:
        if prediction < median_price * 0.85:
            parts.append(
                f"That places it below the training median price of ${median_price:,.0f}."
            )
        elif prediction > median_price * 1.15:
            parts.append(
                f"That places it above the training median price of ${median_price:,.0f}."
            )
        else:
            parts.append(
                f"That places it close to the training median price of ${median_price:,.0f}."
            )

    reason_parts = []
    if extracted.neighborhood:
        reason_parts.append(f"the location in {extracted.neighborhood}")
    if extracted.year_built is not None:
        reason_parts.append(f"the build year of {extracted.year_built}")
    if extracted.garage_cars is not None:
        reason_parts.append(f"the {extracted.garage_cars:,.0f}-car garage")
    if extracted.gr_liv_area is not None:
        reason_parts.append(f"the living area")

    if reason_parts:
        parts.append(
            "The estimate is mainly influenced by "
            + ", ".join(reason_parts[:-1])
            + (f", and {reason_parts[-1]}" if len(reason_parts) > 1 else reason_parts[0])
            + "."
        )

    parts.append(
        f"Overall confidence is {confidence_label} ({confidence_score:.1f}%)."
    )

    missing_all = []
    if missing_critical:
        missing_all.extend(missing_critical)

    optional_missing = [f for f in extracted.missing_features if f not in missing_critical]
    if optional_missing:
        missing_all.extend(optional_missing)

    if missing_all:
        parts.append(
            "Some values were not provided, including "
            + ", ".join(missing_all)
            + ", so the estimate could be improved with more complete property details."
        )

    return " ".join(parts)


def build_interpretation(
    extracted,
    prediction: float,
    confidence_score: float,
    confidence_label: str,
    missing_critical: list[str],
) -> str:
    stats = load_training_stats()
    home_summary = build_home_summary(extracted)

    prompt = f"""
You are a real-estate assistant.

Write a natural interpretation of a house price estimate.

Requirements:
- Write exactly one short paragraph of 4 to 5 sentences.
- Start by describing the home using the extracted features.
- Then explain the estimated price in a natural way.
- Mention useful details from the query such as bedrooms, bathrooms, square footage, garage, build year, and neighborhood when available.
- Mention confidence naturally, not like a system log.
- End the paragraph by mentioning that some values are missing, if any are missing.
- Do not list field names mechanically.
- Do not use bullet points.
- Do not use markdown.
- Do not invent facts.
- The price came from an ML model, so refer to it as an estimate.

Home summary:
{home_summary}

Prediction:
${prediction:,.0f}

Confidence:
{confidence_label} ({confidence_score:.1f}%)

Missing critical fields:
{json.dumps(missing_critical)}

Extracted features:
{json.dumps(extracted.model_dump(), indent=2)}

Training statistics:
{json.dumps(stats, indent=2)}
""".strip()

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        text = getattr(response, "text", "") or ""
        text = clean_text(text)

        if text:
            return text

    except Exception as e:
        print("Gemini error:", e)

    return build_fallback_interpretation(
        extracted,
        prediction,
        confidence_score,
        confidence_label,
        missing_critical,
    )