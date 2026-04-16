# # import re
# # from typing import Optional

# # from app.schemas import ExtractedFeatures

# # EXPECTED_FIELDS = [
# #     "overall_qual",
# #     "gr_liv_area",
# #     "garage_cars",
# #     "total_bsmt_sf",
# #     "full_bath",
# #     "year_built",
# #     "neighborhood",
# #     "bedroom_abvgr",
# #     "kitchen_qual",
# #     "lot_area",
# #     "fireplaces",
# #     "house_style",
# # ]


# # def _search_int(pattern: str, text: str) -> Optional[int]:
# #     match = re.search(pattern, text, flags=re.IGNORECASE)
# #     return int(match.group(1)) if match else None


# # def _search_float(pattern: str, text: str) -> Optional[float]:
# #     match = re.search(pattern, text, flags=re.IGNORECASE)
# #     return float(match.group(1)) if match else None


# # def _search_word(pattern: str, text: str) -> Optional[str]:
# #     match = re.search(pattern, text, flags=re.IGNORECASE)
# #     return match.group(1) if match else None


# # def extract_features_from_query(query: str) -> ExtractedFeatures:
# #     text = query.strip()

# #     bedroom_abvgr = _search_int(r"(\d+)[-\s]*bed(?:room)?s?", text)
# #     full_bath = _search_int(r"(\d+)[-\s]*bath(?:room)?s?", text)
# #     gr_liv_area = _search_float(r"(\d+(?:\.\d+)?)\s*(?:sqft|square feet|sq ft)", text)
# #     garage_cars = _search_float(r"(\d+(?:\.\d+)?)\s*[- ]?car garage", text)
# #     year_built = _search_int(r"(?:built in|year built|built)\s*(\d{4})", text)
# #     lot_area = _search_float(r"lot(?: area)?\s*(?:of\s*)?(\d+(?:\.\d+)?)", text)
# #     fireplaces = _search_int(r"(\d+)\s*fireplaces?", text)
# #     total_bsmt_sf = _search_float(r"(\d+(?:\.\d+)?)\s*(?:sqft|square feet|sq ft)\s*(?:basement|bsmt)", text)

# #     neighborhood = _search_word(r"in\s+([A-Za-z][A-Za-z0-9_]*)", text)
# #     kitchen_qual = _search_word(r"kitchen quality\s*(?:is|=)?\s*(Ex|Gd|TA|Fa|Po)", text)
# #     house_style = _search_word(r"house style\s*(?:is|=)?\s*([A-Za-z0-9]+)", text)
# #     overall_qual = _search_int(r"(?:overall quality|quality)\s*(?:is|=)?\s*(\d+)", text)

# #     extracted_dict = {
# #         "overall_qual": overall_qual,
# #         "gr_liv_area": gr_liv_area,
# #         "garage_cars": garage_cars,
# #         "total_bsmt_sf": total_bsmt_sf,
# #         "full_bath": full_bath,
# #         "year_built": year_built,
# #         "neighborhood": neighborhood,
# #         "bedroom_abvgr": bedroom_abvgr,
# #         "kitchen_qual": kitchen_qual,
# #         "lot_area": lot_area,
# #         "fireplaces": fireplaces,
# #         "house_style": house_style,
# #     }

# #     provided_features = [key for key, value in extracted_dict.items() if value is not None]
# #     missing_features = [key for key in EXPECTED_FIELDS if key not in provided_features]

# #     return ExtractedFeatures(
# #         **extracted_dict,
# #         provided_features=provided_features,
# #         missing_features=missing_features,
# #     )

# import re
# from typing import Optional

# from app.schemas import ExtractedFeatures

# FEATURE_FIELDS = [
#     "overall_qual",
#     "gr_liv_area",
#     "garage_cars",
#     "total_bsmt_sf",
#     "full_bath",
#     "year_built",
#     "neighborhood",
#     "bedroom_abvgr",
#     "kitchen_qual",
#     "lot_area",
#     "fireplaces",
#     "house_style",
# ]


# def _search_int(pattern: str, text: str) -> Optional[int]:
#     match = re.search(pattern, text, flags=re.IGNORECASE)
#     return int(match.group(1)) if match else None


# def _search_float(pattern: str, text: str) -> Optional[float]:
#     match = re.search(pattern, text, flags=re.IGNORECASE)
#     return float(match.group(1)) if match else None


# def _search_word(pattern: str, text: str) -> Optional[str]:
#     match = re.search(pattern, text, flags=re.IGNORECASE)
#     return match.group(1) if match else None


# def refresh_metadata(data: dict) -> ExtractedFeatures:
#     provided = [k for k in FEATURE_FIELDS if data.get(k) is not None]
#     missing = [k for k in FEATURE_FIELDS if data.get(k) is None]

#     data["provided_features"] = provided
#     data["missing_features"] = missing
#     data["confident_features"] = provided.copy()

#     return ExtractedFeatures(**data)


# def extract_features_from_query(query: str) -> ExtractedFeatures:
#     text = query.strip()

#     data = {
#         "overall_qual": _search_int(r"\b(?:overall quality|quality)\s*(?:is|=)?\s*(\d+)\b", text),
#         "gr_liv_area": _search_float(r"(\d+(?:\.\d+)?)\s*(?:sq\s*ft|sqft|square feet|square foot)\b", text),
#         "garage_cars": _search_float(r"(\d+(?:\.\d+)?)\s*[- ]?car garage\b", text),
#         "total_bsmt_sf": _search_float(
#             r"(\d+(?:\.\d+)?)\s*(?:sq\s*ft|sqft|square feet|square foot)\s*(?:basement|bsmt)\b",
#             text,
#         ),
#         "full_bath": _search_int(r"(\d+)\s*[- ]?(?:bath|baths|bathroom|bathrooms)\b", text),
#         "year_built": _search_int(r"(?:built in|built|year built)\s*(\d{4})", text),
#         "neighborhood": _search_word(r"\bin\s+([A-Za-z0-9_]+)\b", text),
#         "bedroom_abvgr": _search_int(r"(\d+)\s*[- ]?(?:bed|beds|bedroom|bedrooms|br)\b", text),
#         "kitchen_qual": _search_word(r"\bkitchen quality\s*(?:is|=)?\s*(Ex|Gd|TA|Fa|Po)\b", text),
#         "lot_area": _search_float(r"\blot(?: area)?\s*(?:of|is|=)?\s*(\d+(?:\.\d+)?)\b", text),
#         "fireplaces": _search_int(r"(\d+)\s*fireplaces?\b", text),
#         "house_style": _search_word(
#             r"\bhouse style\s*(?:is|=)?\s*(1Story|2Story|1\.5Fin|1\.5Unf|SFoyer|SLvl|2\.5Unf|2\.5Fin)\b",
#             text,
#         ),
#     }

#     return refresh_metadata(data)


# def merge_filled_features(extracted: ExtractedFeatures, filled_features: dict | None) -> ExtractedFeatures:
#     data = extracted.model_dump()

#     if filled_features:
#         for key, value in filled_features.items():
#             if key in FEATURE_FIELDS and value not in ("", None):
#                 data[key] = value

#     return refresh_metadata(data)


import json
import re
from typing import Optional

from app.schemas import ExtractedFeatures
from app.llm.gemini_client import client, MODEL_NAME
from app.llm.prompts import EXTRACTOR_PROMPT_V1, EXTRACTOR_PROMPT_V2


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


def refresh_metadata(data: dict) -> ExtractedFeatures:
    provided = [k for k in FEATURE_FIELDS if data.get(k) is not None]
    missing = [k for k in FEATURE_FIELDS if data.get(k) is None]

    confident = data.get("confident_features") or []
    confident = [f for f in confident if f in FEATURE_FIELDS and data.get(f) is not None]

    data["provided_features"] = provided
    data["missing_features"] = missing
    data["confident_features"] = confident if confident else provided.copy()

    return ExtractedFeatures(**data)


def _extract_json_block(text: str) -> dict:
    text = text.strip()
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in Gemini response")
    return json.loads(match.group(0))


def _regex_search_int(pattern: str, text: str) -> Optional[int]:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def _regex_search_float(pattern: str, text: str) -> Optional[float]:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return float(match.group(1)) if match else None


def _regex_search_word(pattern: str, text: str) -> Optional[str]:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1) if match else None


def extract_features_fallback(query: str) -> ExtractedFeatures:
    text = query.strip()

    data = {
        "overall_qual": _regex_search_int(r"\b(?:overall quality|quality)\s*(?:is|=)?\s*(\d+)\b", text),
        "gr_liv_area": _regex_search_float(r"(\d+(?:\.\d+)?)\s*(?:sq\s*ft|sqft|square feet|square foot)\b", text),
        "garage_cars": _regex_search_float(r"(\d+(?:\.\d+)?)\s*[- ]?car garage\b", text),
        "total_bsmt_sf": _regex_search_float(
            r"(\d+(?:\.\d+)?)\s*(?:sq\s*ft|sqft|square feet|square foot)\s*(?:basement|bsmt)\b",
            text,
        ),
        "full_bath": _regex_search_int(r"(\d+)\s*[- ]?(?:bath|baths|bathroom|bathrooms)\b", text),
        "year_built": _regex_search_int(r"(?:built in|built|year built)\s*(\d{4})", text),
        "neighborhood": _regex_search_word(r"\bin\s+([A-Za-z0-9_]+)\b", text),
        "bedroom_abvgr": _regex_search_int(r"(\d+)\s*[- ]?(?:bed|beds|bedroom|bedrooms|br)\b", text),
        "kitchen_qual": _regex_search_word(r"\bkitchen quality\s*(?:is|=)?\s*(Ex|Gd|TA|Fa|Po)\b", text),
        "lot_area": _regex_search_float(r"\blot(?: area)?\s*(?:of|is|=)?\s*(\d+(?:\.\d+)?)\b", text),
        "fireplaces": _regex_search_int(r"(\d+)\s*fireplaces?\b", text),
        "house_style": _regex_search_word(
            r"\bhouse style\s*(?:is|=)?\s*(1Story|2Story|1\.5Fin|1\.5Unf|SFoyer|SLvl|2\.5Unf|2\.5Fin)\b",
            text,
        ),
        "confident_features": [],
    }

    return refresh_metadata(data)


def extract_features_with_gemini(query: str, prompt_version: str = "v2") -> ExtractedFeatures:
    prompt_template = EXTRACTOR_PROMPT_V2 if prompt_version == "v2" else EXTRACTOR_PROMPT_V1
    prompt = prompt_template.format(query=query)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    text = getattr(response, "text", "") or ""
    parsed = _extract_json_block(text)
    return refresh_metadata(parsed)


def extract_features_from_query(query: str, prompt_version: str = "v2") -> ExtractedFeatures:
    try:
        return extract_features_with_gemini(query, prompt_version=prompt_version)
    except Exception:
        return extract_features_fallback(query)


def merge_filled_features(extracted: ExtractedFeatures, filled_features: dict | None) -> ExtractedFeatures:
    data = extracted.model_dump()

    if filled_features:
        for key, value in filled_features.items():
            if key in FEATURE_FIELDS and value not in ("", None):
                data[key] = value

    return refresh_metadata(data)