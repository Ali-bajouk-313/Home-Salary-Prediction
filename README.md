# AI Real Estate Price Estimator

This project predicts residential sale prices from natural-language property descriptions or structured feature inputs. It combines a scikit-learn regression model, a FastAPI backend, a rule-based feature extractor, an optional Gemini-powered explanation layer, and a Streamlit UI for interactive estimates.

## What It Does

- Accepts free-text property descriptions such as "A 3-bedroom house with 2 bathrooms, 1800 sqft, 2-car garage in NAmes built in 2005"
- Extracts supported housing features from the text
- Predicts price with a trained machine learning pipeline
- Returns a confidence score and human-readable interpretation
- Lets users fill missing fields in the Streamlit app and re-run the estimate
- Exposes both natural-language and structured prediction endpoints

## Tech Stack

- FastAPI for the prediction API
- Streamlit for the frontend
- scikit-learn for preprocessing and modeling
- pandas and joblib for data and artifact handling
- Gemini for optional natural-language explanations with a fallback summary when no API key is available

## Project Structure

```text
AI_REAL_STATE/
|-- app/
|   |-- main.py
|   |-- schemas.py
|   |-- llm/
|   |   |-- extractor.py
|   |   |-- interpreter.py
|   |   `-- prompts.py
|   |-- ml/
|   |   |-- predict.py
|   |   `-- train.py
|   `-- utils/
|       `-- confidence.py
|-- artifacts/
|   |-- feature_columns.json
|   `-- model.joblib
|-- data/
|   |-- train.csv
|   `-- test.csv
|-- ui/
|   `-- streamlit_app.py
|-- Dockerfile
|-- requirements.txt
`-- README.md
```

## Supported Features

The model and API use these fields:

- `overall_qual`
- `gr_liv_area`
- `garage_cars`
- `total_bsmt_sf`
- `full_bath`
- `year_built`
- `neighborhood`
- `bedroom_abvgr`
- `kitchen_qual`
- `lot_area`
- `fireplaces`
- `house_style`

Critical fields for stronger predictions:

- `gr_liv_area`
- `bedroom_abvgr`
- `full_bath`
- `year_built`
- `neighborhood`

## Model Summary

The training script compares two candidates:

- Ridge Regression
- Random Forest Regressor

The currently saved best model is `random_forest`.

Saved evaluation metrics from [`artifacts/feature_columns.json`](/c:/Users/USER/OneDrive/Desktop/AI_REAL_STATE/artifacts/feature_columns.json:1):

- Validation RMSE: `24483.55`
- Validation R2: `0.9046`
- Test RMSE: `26674.16`
- Test R2: `0.9065`
- Training median sale price: `$165,000`

## Setup

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Optional environment variables

Create a `.env` file in the project root if you want Gemini-generated explanations:

```env
GEMINI_API_KEY=your_api_key_here
```

If no API key is provided, the app still works and falls back to a locally generated explanation.

## GitHub Commands

Clone an existing repository:

```powershell
git clone <your-repo-url>
cd AI_REAL_STATE
```

Initialize Git in this project if needed:

```powershell
git init
git add .
git commit -m "Initial project setup"
```

Connect the local project to GitHub:

```powershell
git remote add origin <your-repo-url>
git branch -M main
git push -u origin main
```

Common day-to-day commands:

```powershell
git status
git add .
git commit -m "Describe your changes"
git push
```

## Train The Model

If you want to regenerate the saved artifacts:

```powershell
python app/ml/train.py
```

This writes:

- `artifacts/model.joblib`
- `artifacts/feature_columns.json`

## Run The API

```powershell
uvicorn app.main:app --reload
```

Open:

- Swagger docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/`

## Run The Streamlit App

Start the API first, then run:

```powershell
streamlit run ui/streamlit_app.py
```

## API Endpoints

### `GET /`

Health check response:

```json
{
  "status": "ok"
}
```

### `POST /predict`

Request:

```json
{
  "query": "A 3-bedroom house with 2 bathrooms, 1800 sqft, 2-car garage in NAmes built in 2005"
}
```

### `POST /predict_from_features`

Request:

```json
{
  "features": {
    "gr_liv_area": 1800,
    "bedroom_abvgr": 3,
    "full_bath": 2,
    "year_built": 2005,
    "neighborhood": "NAmes"
  }
}
```

Typical response shape:

```json
{
  "extracted_features": {},
  "prediction": 215000.0,
  "interpretation": "Estimated value summary...",
  "missing_fields_needed": [],
  "confidence_score": 82.5,
  "confidence_label": "high",
  "status": "success"
}
```

Possible `status` values:

- `success`
- `partial_success`
- `needs_more_info`
- `error`

## Streamlit Workflow

The UI supports a two-step flow:

1. Enter a natural-language property description
2. Review the extracted features, prediction, confidence, and explanation
3. Fill in any missing features
4. Re-run the prediction with the completed values

## Docker

Build the image:

```powershell
docker build -t real-estate-ai .
```

Run the container:

```powershell
docker run --env-file .env -p 8000:8000 real-estate-ai
```

Then open:

- `http://127.0.0.1:8000/docs`
  http://localhost:8001/docs for FastAPI
  for both Streamlit and FastAPI
  docker compose up --build

http://localhost:8501

## Notes

- The feature extractor is currently rule-based using regular expressions, not an LLM extraction pipeline
- Gemini is used only for explanation text, not for the price prediction itself
- Predictions become less reliable when important fields are missing
- The dataset and features are based on the Ames housing problem
  FAST API
  docker build -t real-estate-backend .
  docker run --name backend-test -p 8001:8000 --env-file .env real-estate-backend
  http://localhost:8001/docs

STREAMLIT
docker build -t real-estate-streamlit -f Dockerfile.streamlit .
docker run --name streamlit-test -p 8501:8501 -e API_PREDICT_URL=http://host.docker.internal:8001/predict -e API_FEATURES_URL=http://host.

docker.internal:8001/predict_from_features real-estate-streamlit
http://localhost:8501/

docker run --env-file .env -p 8000:8000 real-estate-ai
