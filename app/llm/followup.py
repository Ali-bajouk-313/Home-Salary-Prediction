import json

from app.llm.gemini_client import client, MODEL_NAME
from app.llm.prompts import FOLLOWUP_PROMPT


def build_follow_up_prompt(query: str, extracted, missing_fields: list[str]) -> str:
    if not missing_fields:
        return ""

    prompt = FOLLOWUP_PROMPT.format(
        query=query,
        features_json=json.dumps(extracted.model_dump(), indent=2),
        missing_fields=", ".join(missing_fields),
    )

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        text = getattr(response, "text", "") or ""
        return text.strip() if text else ""
    except Exception:
        return (
            "I found some property details, but a few important values are still missing. "
            "Would you like to fill them in before I run the prediction?"
        )