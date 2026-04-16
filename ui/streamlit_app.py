import requests
import streamlit as st

API_PREDICT_URL = "http://127.0.0.1:8000/predict"
API_FEATURES_URL = "http://127.0.0.1:8000/predict_from_features"

FEATURE_LABELS = {
    "overall_qual": "Overall Quality (1-10)",
    "gr_liv_area": "Ground Living Area (sqft)",
    "garage_cars": "Garage Capacity (cars)",
    "total_bsmt_sf": "Total Basement Area (sqft)",
    "full_bath": "Full Bathrooms",
    "year_built": "Year Built",
    "neighborhood": "Neighborhood",
    "bedroom_abvgr": "Bedrooms Above Ground",
    "kitchen_qual": "Kitchen Quality",
    "lot_area": "Lot Area",
    "fireplaces": "Fireplaces",
    "house_style": "House Style",
}

NUMERIC_INT_FIELDS = {
    "overall_qual",
    "full_bath",
    "year_built",
    "bedroom_abvgr",
    "fireplaces",
}

NUMERIC_FLOAT_FIELDS = {
    "gr_liv_area",
    "garage_cars",
    "total_bsmt_sf",
    "lot_area",
}

KITCHEN_QUAL_OPTIONS = ["Ex", "Gd", "TA", "Fa", "Po"]

HOUSE_STYLE_OPTIONS = [
    "1Story",
    "2Story",
    "1.5Fin",
    "1.5Unf",
    "SFoyer",
    "SLvl",
    "2.5Unf",
    "2.5Fin",
]

NEIGHBORHOOD_OPTIONS = [
    "Blmngtn",
    "Blueste",
    "BrDale",
    "BrkSide",
    "ClearCr",
    "CollgCr",
    "Crawfor",
    "Edwards",
    "Gilbert",
    "IDOTRR",
    "MeadowV",
    "Mitchel",
    "NAmes",
    "NoRidge",
    "NPkVill",
    "NridgHt",
    "NWAmes",
    "OldTown",
    "Sawyer",
    "SawyerW",
    "Somerst",
    "StoneBr",
    "SWISU",
    "Timber",
    "Veenker",
]

NO_SELECTION = "-- Select --"


def confidence_badge(label: str) -> str:
    label = (label or "low").lower()
    if label == "high":
        return "🟢 High"
    if label == "medium":
        return "🟡 Medium"
    return "🔴 Low"


def render_result(data: dict):
    status = data.get("status", "unknown")
    prediction = data.get("prediction")
    interpretation = data.get("interpretation", "")
    extracted_features = data.get("extracted_features", {})
    missing_fields_needed = data.get("missing_fields_needed", [])
    confidence_score = float(data.get("confidence_score", 0.0))
    confidence_label = data.get("confidence_label", "low")

    st.subheader("Status")
    if status == "success":
        st.success(status)
    elif status == "partial_success":
        st.warning(status)
    elif status == "needs_more_info":
        st.info(status)
    else:
        st.error(status)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Predicted Price")
        if prediction is not None:
            st.success(f"${prediction:,.2f}")
        else:
            st.write("Not available")

    with col2:
        st.subheader("Confidence")
        st.metric("Score", f"{confidence_score:.1f}%")
        st.write(confidence_badge(confidence_label))

    if missing_fields_needed:
        st.subheader("Missing Critical Fields")
        st.write(", ".join(missing_fields_needed))

    st.subheader("Interpretation")
    st.write(interpretation)

    st.subheader("Extracted Features")
    st.json(extracted_features)


def selectbox_with_empty(label: str, options: list[str], current_val):
    full_options = [NO_SELECTION] + options
    index = full_options.index(current_val) if current_val in full_options else 0
    selected = st.selectbox(label, options=full_options, index=index)
    return None if selected == NO_SELECTION else selected


def get_missing_feature_input(field: str, updated_features: dict):
    label = FEATURE_LABELS.get(field, field)
    current_val = updated_features.get(field)

    if field in NUMERIC_INT_FIELDS:
        raw_value = st.text_input(label, value="" if current_val is None else str(current_val))
        if raw_value.strip() == "":
            return None
        try:
            return int(raw_value)
        except ValueError:
            st.warning(f"{label} should be an integer.")
            return None

    if field in NUMERIC_FLOAT_FIELDS:
        raw_value = st.text_input(label, value="" if current_val is None else str(current_val))
        if raw_value.strip() == "":
            return None
        try:
            return float(raw_value)
        except ValueError:
            st.warning(f"{label} should be a number.")
            return None

    if field == "kitchen_qual":
        return selectbox_with_empty(label, KITCHEN_QUAL_OPTIONS, current_val)

    if field == "house_style":
        return selectbox_with_empty(label, HOUSE_STYLE_OPTIONS, current_val)

    if field == "neighborhood":
        return selectbox_with_empty(label, NEIGHBORHOOD_OPTIONS, current_val)

    raw_value = st.text_input(label, value=current_val or "")
    return raw_value.strip() if raw_value.strip() else None


st.set_page_config(page_title="AI Real Estate Agent", layout="centered")

st.title("AI Real Estate Agent")
st.caption(
    "Describe a property in natural language. The app extracts features, "
    "predicts price, and lets you fill missing values to improve the estimate."
)

with st.expander("Example queries"):
    st.code(
        "A 3-bedroom house with 2 bathrooms, 1800 sqft, 2-car garage in NAmes built in 2005",
        language="text",
    )
    st.code(
        "4 bedroom house with 2 bathrooms in CollgCr built in 1998",
        language="text",
    )
    st.code(
        "2 bedroom apartment in NAmes",
        language="text",
    )

query = st.text_area(
    "Describe the property",
    placeholder=(
        "Example: A 3-bedroom house with 2 bathrooms, 1800 sqft, "
        "2-car garage in NAmes built in 2005"
    ),
    height=140,
)

if "prediction_data" not in st.session_state:
    st.session_state.prediction_data = None

if st.button("Estimate Price", use_container_width=True):
    if not query.strip():
        st.warning("Please enter a property description.")
    else:
        try:
            with st.spinner("Estimating price..."):
                response = requests.post(
                    API_PREDICT_URL,
                    json={"query": query},
                    timeout=60,
                )
                response.raise_for_status()
                st.session_state.prediction_data = response.json()
        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to the FastAPI server. "
                "Start it first with: uvicorn app.main:app --reload"
            )
        except requests.exceptions.Timeout:
            st.error("The request timed out. Please try again.")
        except requests.exceptions.HTTPError as e:
            st.error(f"API error: {e}")
        except Exception as e:
            st.error(f"Request failed: {e}")

if st.session_state.prediction_data:
    render_result(st.session_state.prediction_data)

    extracted = st.session_state.prediction_data.get("extracted_features", {})
    missing_features = extracted.get("missing_features", [])

    if missing_features:
        st.divider()
        st.subheader("Fill Missing Features")

        fill_missing = st.radio(
            "Do you want to fill the missing features and re-predict?",
            ["No", "Yes"],
            horizontal=True,
        )

        if fill_missing == "Yes":
            updated_features = extracted.copy()

            with st.form("fill_missing_form"):
                for field in missing_features:
                    updated_features[field] = get_missing_feature_input(field, updated_features)

                submitted = st.form_submit_button("Re-predict", use_container_width=True)

            if submitted:
                cleaned_features = {}
                for key, value in updated_features.items():
                    if key in ["provided_features", "missing_features"]:
                        continue
                    cleaned_features[key] = value

                try:
                    with st.spinner("Recalculating with filled values..."):
                        response = requests.post(
                            API_FEATURES_URL,
                            json={"features": cleaned_features},
                            timeout=60,
                        )
                        response.raise_for_status()
                        st.session_state.prediction_data = response.json()
                        st.rerun()
                except requests.exceptions.ConnectionError:
                    st.error(
                        "Could not connect to the FastAPI server. "
                        "Start it first with: uvicorn app.main:app --reload"
                    )
                except requests.exceptions.Timeout:
                    st.error("The re-prediction request timed out. Please try again.")
                except requests.exceptions.HTTPError as e:
                    st.error(f"API error during re-prediction: {e}")
                except Exception as e:
                    st.error(f"Re-prediction failed: {e}")
                