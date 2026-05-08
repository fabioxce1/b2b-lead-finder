from typing import Optional
from openai import OpenAI
from models import MatchResult, UseCase


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
        client = OpenAI(api_key=api_key)

        top_companies = results[:5]
        companies_context = []
        for r in top_companies:
            companies_context.append(
                f"- {r.company.name} ({r.company.industry}, {r.company.location}): "
                f"Pain points: {', '.join(r.company.pain_points)}. "
                f"Presupuesto: {r.company.budget_range}. "
                f"Etapa: {r.company.growth_stage}. "
                f"Decisores: {', '.join(r.company.decision_makers)}."
            )

        prompt = f"""Eres un experto en desarrollo de negocios B2B. Analiza la siguiente situación:

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

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
        )

        import json
        content = response.choices[0].message.content
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
