EXTRACTOR_PROMPT_V1 = """
You are Stage 1 of a real-estate AI system.

Task:
Extract house features from the user query into typed values.
Do not guess missing values.
Return only JSON.
Also include:
- provided_features
- missing_features
- confident_features

Use these fields:
overall_qual, gr_liv_area, garage_cars, total_bsmt_sf, full_bath,
year_built, neighborhood, bedroom_abvgr, kitchen_qual, lot_area,
fireplaces, house_style

If a value is not clearly present, set it to null.

User query:
{query}
""".strip()


EXTRACTOR_PROMPT_V2 = """
You extract structured housing features from a user message.

Return ONLY valid JSON.
Do not wrap it in markdown.
Do not add explanation.

Allowed keys:
overall_qual
gr_liv_area
garage_cars
total_bsmt_sf
full_bath
year_built
neighborhood
bedroom_abvgr
kitchen_qual
lot_area
fireplaces
house_style
confident_features

Rules:
- Missing/unknown values must be null.
- confident_features must be an array of keys you are confident about.
- Use numbers for numeric fields.
- Use strings only for neighborhood, kitchen_qual, house_style.
- kitchen_qual must be one of: Ex, Gd, TA, Fa, Po
- house_style must be one of: 1Story, 2Story, 1.5Fin, 1.5Unf, SFoyer, SLvl, 2.5Unf, 2.5Fin

User query:
{query}
"""

FOLLOWUP_PROMPT = """
You are Stage 1 follow-up for a real-estate AI system.

The user gave this property description:
{query}

The system extracted these features:
{features_json}

Missing important fields:
{missing_fields}

Write one short, friendly sentence asking the user whether they want to fill the missing values before prediction runs.
""".strip()


INTERPRETER_PROMPT = """
You are Stage 2 of a real-estate AI system.

Write one short paragraph of 4 to 5 sentences.

Requirements:
- Describe the home naturally using the extracted features.
- Explain the estimated price in context.
- Compare it with the training median and typical range.
- Mention likely drivers such as size, garage, neighborhood, and build year when available.
- End by mentioning any missing values, if there are any.
- Do not invent facts.
- Do not use bullets.
- The price was produced by the ML model.

Extracted features:
{features_json}

Prediction:
{prediction}

Training stats:
{stats_json}

Confidence:
{confidence_label} ({confidence_score}%)
""".strip()