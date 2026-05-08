import json
import os
from typing import Optional
from models import Company, MatchResult

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_companies.json")

INDUSTRY_MAP = {
    "tecnologia": ["Tecnología", "Tecnología", "Tecnología"],
    "tech": ["Tecnología", "Tecnología", "Tecnología"],
    "software": ["Tecnología", "Tecnología"],
    "marketing": ["Marketing", "Marketing"],
    "publicidad": ["Marketing", "Entretenimiento"],
    "salud": ["Salud", "Farmacéutica"],
    "medicina": ["Salud"],
    "educacion": ["Educación"],
    "construccion": ["Construcción"],
    "retail": ["Retail"],
    "comercio": ["Retail"],
    "agricultura": ["Agricultura"],
    "agro": ["Agricultura"],
    "finanzas": ["Finanzas"],
    "fintech": ["Finanzas"],
    "logistica": ["Logística"],
    "transporte": ["Logística"],
    "entretenimiento": ["Entretenimiento"],
    "energia": ["Energía"],
    "solar": ["Energía"],
    "automotriz": ["Automotriz"],
    "turismo": ["Turismo"],
    "hoteleria": ["Turismo"],
    "farmaceutica": ["Farmacéutica"],
    "legal": ["Legal"],
    "abogacia": ["Legal"],
    "consultoria": ["Consultoría"],
    "alimentos": ["Alimentos"],
    "comida": ["Alimentos"],
}

SIZE_MAP = {
    "pequena": "Pequeña",
    "pequeña": "Pequeña",
    "small": "Pequeña",
    "mediana": "Mediana",
    "medium": "Mediana",
    "grande": "Grande",
    "large": "Grande",
    "enterprise": "Grande",
}


def load_companies() -> list[Company]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Company(**item) for item in data]


def normalize_text(text: str) -> str:
    return text.lower().strip()


def find_industry_matches(specialization: str) -> list[str]:
    spec = normalize_text(specialization)
    matched = set()
    for key, industries in INDUSTRY_MAP.items():
        if key in spec:
            matched.update(industries)
    return list(matched)


def find_size_matches(target_audience: str) -> Optional[str]:
    audience = normalize_text(target_audience)
    for key, size in SIZE_MAP.items():
        if key in audience:
            return size
    return None


def calculate_match_score(
    company: Company,
    specialization: str,
    target_audience: str,
    location: str,
) -> tuple[float, list[str]]:
    score = 0.0
    factors = []

    industry_matches = find_industry_matches(specialization)
    if company.industry in industry_matches:
        score += 30
        factors.append(f"Industria {company.industry} alineada con tu especialización")

    spec_lower = normalize_text(specialization)
    for pain in company.pain_points:
        pain_lower = normalize_text(pain)
        if any(word in pain_lower for word in spec_lower.split()):
            score += 15
            factors.append(f"Necesidad detectada: {pain}")
            break

    size_match = find_size_matches(target_audience)
    if size_match and company.size == size_match:
        score += 15
        factors.append(f"Tamaño de empresa ({company.size}) coincide con tu público objetivo")

    loc_lower = normalize_text(location)
    if loc_lower:
        if normalize_text(company.country) in loc_lower or normalize_text(company.city) in loc_lower:
            score += 25
            factors.append(f"Ubicación {company.location} coincide con tu búsqueda")
        elif any(word in normalize_text(company.location) for word in loc_lower.split()):
            score += 10
            factors.append(f"Ubicación {company.location} relacionada con tu búsqueda")

    if company.growth_stage == "expansión":
        score += 10
        factors.append("Empresa en expansión = mayor probabilidad de inversión")
    elif company.growth_stage == "crecimiento":
        score += 5
        factors.append("Empresa en crecimiento = oportunidad de partnership")

    if company.budget_range == "alto":
        score += 10
        factors.append("Presupuesto alto disponible")
    elif company.budget_range == "medio":
        score += 5

    score = min(score, 100)
    return score, factors


def search_companies(
    specialization: str,
    target_audience: str,
    location: str,
) -> list[MatchResult]:
    companies = load_companies()
    results = []

    for company in companies:
        score, factors = calculate_match_score(
            company, specialization, target_audience, location
        )

        if score > 0:
            probability = min(score * 0.85, 95)

            if score >= 70:
                opportunity = "Alta"
            elif score >= 45:
                opportunity = "Media"
            else:
                opportunity = "Baja"

            recommendation = generate_recommendation(company, score, factors)

            results.append(
                MatchResult(
                    company=company,
                    match_score=round(score, 1),
                    probability=round(probability, 1),
                    opportunity_level=opportunity,
                    matching_factors=factors,
                    recommendation=recommendation,
                )
            )

    results.sort(key=lambda x: x.match_score, reverse=True)
    return results


def generate_recommendation(company: Company, score: float, factors: list[str]) -> str:
    if score >= 70:
        return f"Contacto prioritario. {company.name} tiene necesidades claras que puedes resolver. Enfócate en los decisores: {', '.join(company.decision_makers)}."
    elif score >= 45:
        return f"Oportunidad viable. Prepara una propuesta de valor específica para {company.industry}. Considera abordar a {company.decision_makers[0]}."
    else:
        return f"Oportunidad a largo plazo. {company.name} podría beneficiarse de tus servicios en el futuro. Mantén seguimiento."
