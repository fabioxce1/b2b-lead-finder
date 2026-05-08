import json
from typing import Optional
import google.generativeai as genai
from models import MatchResult, UseCase, SpecificOpportunity


def generate_ai_analysis(
    specialization: str,
    target_audience: str,
    location: str,
    results: list[MatchResult],
    api_key: Optional[str] = None,
) -> tuple[dict, list[UseCase]]:
    if not api_key:
        return _fallback_analysis(specialization, results)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        top_companies = results[:5]
        companies_context = []
        for r in top_companies:
            website_info = ""
            if r.company.website_content:
                website_info = f"\n   Contenido web: {r.company.website_content[:1000]}..."

            companies_context.append(
                f"- {r.company.name} ({r.company.industry}, {r.company.location}): "
                f"Descripción: {r.company.description}. "
                f"Pain points: {', '.join(r.company.pain_points)}. "
                f"Presupuesto: {r.company.budget_range}. "
                f"Etapa: {r.company.growth_stage}. "
                f"Decisores: {', '.join(r.company.decision_makers)}.{website_info}"
            )

        prompt = f"""Eres un experto en desarrollo de negocios B2B y consultoría tecnológica. Analiza la siguiente situación:

ESPECIALIZACIÓN DEL PROVEEDOR: {specialization}
PÚBLICO OBJETIVO: {target_audience}
UBICACIÓN: {location}

EMPRESAS POTENCIALES (top {len(top_companies)}):
{chr(10).join(companies_context)}

Genera:
1. Un resumen ejecutivo con: total_oportunidades, alta_prioridad, media_prioridad, baja_prioridad, industria_mas_prometedora, recomendacion_general
2. Casos de uso puntuales para las top 3 empresas donde el proveedor pueda suplir necesidades específicas.

Responde SOLO con JSON en este formato exacto:
{{
  "summary": {{
    "total_oportunidades": <numero>,
    "alta_prioridad": <numero>,
    "media_prioridad": <numero>,
    "baja_prioridad": <numero>,
    "industria_mas_prometedora": "<string>",
    "recomendacion_general": "<string>"
  }},
  "use_cases": [
    {{
      "company_name": "<nombre empresa>",
      "scenario": "<descripción del escenario>",
      "how_to_approach": "<cómo acercarse al cliente>",
      "value_proposition": "<propuesta de valor específica>",
      "expected_outcome": "<resultado esperado>",
      "urgency": "<alta|media|baja>"
    }}
  ]
}}"""

        response = model.generate_content(prompt)
        content = response.text

        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            content = content[json_start:json_end]

        data = json.loads(content)

        summary = data.get("summary", {})
        use_cases_data = data.get("use_cases", [])

        use_cases = [
            UseCase(
                company_name=uc["company_name"],
                scenario=uc["scenario"],
                how_to_approach=uc["how_to_approach"],
                value_proposition=uc["value_proposition"],
                expected_outcome=uc["expected_outcome"],
                urgency=uc["urgency"],
            )
            for uc in use_cases_data
        ]

        return summary, use_cases

    except Exception:
        return _fallback_analysis(specialization, results)


async def analyze_company_opportunities(
    company: MatchResult,
    specialization: str,
    api_key: str,
) -> tuple[list[SpecificOpportunity], str]:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        website_info = ""
        if company.company.website_content:
            website_info = f"""
CONTENIDO DEL SITIO WEB DE LA EMPRESA:
{company.company.website_content[:3000]}
"""

        prompt = f"""Eres un consultor tecnológico experto. Analiza cómo un profesional con la siguiente especialización puede ayudar a esta empresa:

ESPECIALIZACIÓN DEL PROVEEDOR: {specialization}

EMPRESA: {company.company.name}
INDUSTRIA: {company.company.industry}
UBICACIÓN: {company.company.location}
DESCRIPCIÓN: {company.company.description}
PAIN POINTS: {', '.join(company.company.pain_points)}
DECISORES: {', '.join(company.company.decision_makers)}
{website_info}

Responde SOLO con JSON en este formato:
{{
  "opportunities": [
    {{
      "title": "<título corto de la oportunidad>",
      "description": "<descripción detallada de cómo aplicar la especialización a esta empresa>",
      "impact": "<alto|medio|bajo>",
      "effort": "<alto|medio|bajo>",
      "urgency": "<alta|media|baja>"
    }}
  ],
  "analysis": "<análisis general de 2-3 oraciones sobre las oportunidades tecnológicas de esta empresa>"
}}

Genera entre 3 y 6 oportunidades específicas y concretas."""

        response = model.generate_content(prompt)
        content = response.text

        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            content = content[json_start:json_end]

        data = json.loads(content)

        opportunities = [
            SpecificOpportunity(
                title=opp["title"],
                description=opp["description"],
                impact=opp["impact"],
                effort=opp["effort"],
                urgency=opp["urgency"],
            )
            for opp in data.get("opportunities", [])
        ]

        analysis = data.get("analysis", "")

        return opportunities, analysis

    except Exception:
        return [], ""


def _fallback_analysis(
    specialization: str, results: list[MatchResult]
) -> tuple[dict, list[UseCase]]:
    alta = sum(1 for r in results if r.opportunity_level == "Alta")
    media = sum(1 for r in results if r.opportunity_level == "Media")
    baja = sum(1 for r in results if r.opportunity_level == "Baja")

    industries = {}
    for r in results:
        industries[r.company.industry] = industries.get(r.company.industry, 0) + 1
    top_industry = max(industries, key=industries.get) if industries else "N/A"

    summary = {
        "total_oportunidades": len(results),
        "alta_prioridad": alta,
        "media_prioridad": media,
        "baja_prioridad": baja,
        "industria_mas_prometedora": top_industry,
        "recomendacion_general": f"Enfócate en las {alta} empresas de alta prioridad. Tu especialización en {specialization} tiene demanda en el mercado. Prepara propuestas personalizadas para cada sector.",
    }

    use_cases = []
    for r in results[:3]:
        use_cases.append(
            UseCase(
                company_name=r.company.name,
                scenario=f"{r.company.name} necesita resolver: {'; '.join(r.company.pain_points[:2])}",
                how_to_approach=f"Contactar a {r.company.decision_makers[0]} con un caso de éxito relevante a su industria {r.company.industry}",
                value_proposition=f"Ofrecer {specialization} para resolver sus pain points específicos con un ROI medible",
                expected_outcome=f"Generar interés en una reunión de descubrimiento y cerrar un proyecto piloto",
                urgency="alta" if r.match_score >= 70 else "media",
            )
        )

    return summary, use_cases
