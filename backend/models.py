from pydantic import BaseModel
from typing import Optional


class SearchRequest(BaseModel):
    specialization: str
    target_audience: str
    location: str
    google_places_api_key: Optional[str] = None
    serp_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    deep_analysis: bool = False
    manual_companies: list[dict] = []


class Company(BaseModel):
    id: int
    name: str
    industry: str
    size: str
    employees: int
    location: str
    country: str
    city: str
    description: str
    website: str
    pain_points: list[str] = []
    budget_range: str = "medio"
    decision_makers: list[str] = []
    growth_stage: str = "estable"
    source: str = "sample"
    rating: float = 0
    website_content: str = ""


class SpecificOpportunity(BaseModel):
    title: str
    description: str
    impact: str
    effort: str
    urgency: str


class MatchResult(BaseModel):
    company: Company
    match_score: float
    probability: float
    opportunity_level: str
    matching_factors: list[str]
    recommendation: str
    specific_opportunities: list[SpecificOpportunity] = []
    ai_analysis: str = ""


class UseCase(BaseModel):
    company_name: str
    scenario: str
    how_to_approach: str
    value_proposition: str
    expected_outcome: str
    urgency: str


class AnalysisResponse(BaseModel):
    results: list[MatchResult]
    summary: dict
    use_cases: list[UseCase]


class ValidateKeyRequest(BaseModel):
    api_key: str


class ValidateKeyResponse(BaseModel):
    valid: bool
    message: str
