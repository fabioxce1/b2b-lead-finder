from pydantic import BaseModel
from typing import Optional


class SearchRequest(BaseModel):
    specialization: str
    target_audience: str
    location: str
    openai_api_key: Optional[str] = None


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
    pain_points: list[str]
    budget_range: str
    decision_makers: list[str]
    growth_stage: str


class MatchResult(BaseModel):
    company: Company
    match_score: float
    probability: float
    opportunity_level: str
    matching_factors: list[str]
    recommendation: str


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
