from typing import Optional, List,Dict
from pydantic import BaseModel, Field


class ExtractedFeatures(BaseModel):
    overall_qual: Optional[int] = Field(None, ge=1, le=10)
    gr_liv_area: Optional[float] = Field(None, ge=0)
    garage_cars: Optional[float] = Field(None, ge=0)
    total_bsmt_sf: Optional[float] = Field(None, ge=0)
    full_bath: Optional[int] = Field(None, ge=0)
    year_built: Optional[int] = Field(None, ge=1800, le=2100)
    neighborhood: Optional[str] = None
    bedroom_abvgr: Optional[int] = Field(None, ge=0)
    kitchen_qual: Optional[str] = None
    lot_area: Optional[float] = Field(None, ge=0)
    fireplaces: Optional[int] = Field(None, ge=0)
    house_style: Optional[str] = None

    provided_features: List[str] = []
    missing_features: List[str] = []
    confident_features: List[str] = Field(default_factory=list)


class UserQuery(BaseModel):
    query: str


class StructuredPredictionRequest(BaseModel):
    features: ExtractedFeatures


class PredictionResponse(BaseModel):
    extracted_features: ExtractedFeatures
    prediction: Optional[float] = None
    interpretation: str
    missing_fields_needed: List[str] = []
    confidence_score: float = 0.0
    confidence_label: str = "low"
    status: str = "success"
    training_stats: Dict[str, Optional[float]] = Field(default_factory=dict)