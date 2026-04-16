# # import json
# # from pathlib import Path
# # from typing import Any

# # from pydantic import ValidationError

# # from app.schemas import ExtractedFeatures
# # from app.llm.prompts import EXTRACTOR_PROMPT_V1, EXTRACTOR_PROMPT_V2


# # TEST_QUERIES = [
# #     "Nice house",
# #     "2 bedroom apartment in NAmes",
# #     "A 3-bedroom house with 2 bathrooms, 1800 sqft, 2-car garage in NAmes built in 2005",
# #     "4 bedroom house with 2 bathrooms in CollgCr built in 1998",
# # ]


# # def mock_llm_extract(query: str, prompt_version: str) -> dict[str, Any]:
# #     """
# #     Temporary stand-in for real LLM extraction.

# #     Replace this with your Gemini extraction call later if needed.
# #     For now, we call your existing extractor logic so the evaluation pipeline exists.
# #     """
# #     from app.llm.extractor import extract_features_from_query

# #     extracted = extract_features_from_query(query)
# #     data = extracted.model_dump()
# #     data.pop("provided_features", None)
# #     data.pop("missing_features", None)
# #     return data


# # def validate_output(output: dict[str, Any]) -> tuple[bool, str]:
# #     try:
# #         ExtractedFeatures(**output)
# #         return True, "valid"
# #     except ValidationError as e:
# #         return False, str(e)


# # def main():
# #     prompts = {
# #         "v1": EXTRACTOR_PROMPT_V1,
# #         "v2": EXTRACTOR_PROMPT_V2,
# #     }

# #     results = []

# #     for version, prompt_template in prompts.items():
# #         for query in TEST_QUERIES:
# #             prompt = prompt_template.format(query=query)

# #             try:
# #                 output = mock_llm_extract(query, version)
# #                 is_valid, validation_msg = validate_output(output)
# #             except Exception as e:
# #                 output = {"error": str(e)}
# #                 is_valid = False
# #                 validation_msg = str(e)

# #             results.append(
# #                 {
# #                     "version": version,
# #                     "input": query,
# #                     "prompt_preview": prompt[:300],
# #                     "output": output,
# #                     "validation_result": validation_msg,
# #                     "is_valid": is_valid,
# #                 }
# #             )

# #     out_path = Path("artifacts/prompt_eval_results.json")
# #     out_path.parent.mkdir(exist_ok=True)
# #     with open(out_path, "w", encoding="utf-8") as f:
# #         json.dump(results, f, indent=2)

# #     valid_counts = {}
# #     for version in prompts:
# #         valid_counts[version] = sum(
# #             1 for r in results if r["version"] == version and r["is_valid"]
# #         )

# #     summary_path = Path("artifacts/prompt_eval_summary.md")
# #     with open(summary_path, "w", encoding="utf-8") as f:
# #         f.write("# Prompt Evaluation Summary\n\n")
# #         for version, count in valid_counts.items():
# #             f.write(f"- **{version}**: {count}/{len(TEST_QUERIES)} valid outputs\n")
# #         winner = max(valid_counts, key=valid_counts.get)
# #         f.write(f"\n## Winner\n\n**{winner}** selected based on validation success.\n")

# #     print("Saved:")
# #     print(f"- {out_path}")
# #     print(f"- {summary_path}")


# # if __name__ == "__main__":
# #     main()

# import json
# from pathlib import Path
# from pydantic import ValidationError

# from app.schemas import ExtractedFeatures
# from app.llm.prompts import EXTRACTOR_PROMPT_V1, EXTRACTOR_PROMPT_V2
# from app.llm.extractor import extract_features_from_query

# TEST_QUERIES = [
#     "Nice house",
#     "2 bedroom apartment in NAmes",
#     "A 3-bedroom house with 2 bathrooms, 1800 sqft, 2-car garage in NAmes built in 2005",
#     "4 bedroom house with 2 bathrooms in CollgCr built in 1998",
# ]


# def validate_output(output):
#     try:
#         ExtractedFeatures(**output)
#         return True, "valid"
#     except ValidationError as e:
#         return False, str(e)


# def main():
#     prompts = {
#         "v1": EXTRACTOR_PROMPT_V1,
#         "v2": EXTRACTOR_PROMPT_V2,
#     }

#     results = []

#     for version, prompt_template in prompts.items():
#         for query in TEST_QUERIES:
#             prompt_preview = prompt_template.format(query=query)

#             extracted = extract_features_from_query(query)
#             output = extracted.model_dump()
#             output.pop("provided_features", None)
#             output.pop("missing_features", None)
#             output.pop("confident_features", None)

#             is_valid, validation_result = validate_output(output)

#             results.append(
#                 {
#                     "version": version,
#                     "input": query,
#                     "prompt_preview": prompt_preview[:300],
#                     "output": output,
#                     "validation_result": validation_result,
#                     "is_valid": is_valid,
#                 }
#             )

#     Path("artifacts").mkdir(exist_ok=True)

#     with open("artifacts/prompt_eval_results.json", "w", encoding="utf-8") as f:
#         json.dump(results, f, indent=2)

#     counts = {
#         version: sum(1 for r in results if r["version"] == version and r["is_valid"])
#         for version in prompts
#     }
#     winner = max(counts, key=counts.get)

#     with open("artifacts/prompt_eval_summary.md", "w", encoding="utf-8") as f:
#         f.write("# Prompt Evaluation Summary\n\n")
#         for version, count in counts.items():
#             f.write(f"- **{version}**: {count}/{len(TEST_QUERIES)} valid outputs\n")
#         f.write(f"\n## Winner\n\n**{winner}** selected based on validation success.\n")

#     print("Saved prompt evaluation files in artifacts/")


# if __name__ == "__main__":
#     main()


# app/llm/evaluate_prompts.py
import json
from pathlib import Path
from pydantic import ValidationError

from app.schemas import ExtractedFeatures
from app.llm.prompts import EXTRACTOR_PROMPT_V1, EXTRACTOR_PROMPT_V2
from app.llm.extractor import extract_features_with_gemini

TEST_QUERIES = [
    "Nice house",
    "2 bedroom apartment in NAmes",
    "A 3-bedroom house with 2 bathrooms, 1800 sqft, 2-car garage in NAmes built in 2005",
    "4 bedroom house with 2 bathrooms in CollgCr built in 1998",
]


def validate_output(output):
    try:
        ExtractedFeatures(**output)
        return True, "valid"
    except ValidationError as e:
        return False, str(e)


def main():
    prompts = {"v1": EXTRACTOR_PROMPT_V1, "v2": EXTRACTOR_PROMPT_V2}
    results = []

    for version in prompts:
        for query in TEST_QUERIES:
            try:
                extracted = extract_features_with_gemini(query, prompt_version=version)
                output = extracted.model_dump()
                is_valid, validation_result = validate_output(output)
            except Exception as e:
                output = {"error": str(e)}
                is_valid = False
                validation_result = str(e)

            results.append(
                {
                    "version": version,
                    "input": query,
                    "output": output,
                    "validation_result": validation_result,
                    "is_valid": is_valid,
                }
            )

    Path("artifacts").mkdir(exist_ok=True)

    with open("artifacts/prompt_eval_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    counts = {
        version: sum(1 for r in results if r["version"] == version and r["is_valid"])
        for version in prompts
    }
    winner = max(counts, key=counts.get)

    with open("artifacts/prompt_eval_summary.md", "w", encoding="utf-8") as f:
        f.write("# Prompt Evaluation Summary\n\n")
        for version, count in counts.items():
            f.write(f"- **{version}**: {count}/{len(TEST_QUERIES)} valid outputs\n")
        f.write(f"\n## Winner\n\n**{winner}** selected based on validation success.\n")

    print("Saved prompt evaluation files in artifacts/")


if __name__ == "__main__":
    main()