from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import random
import google.generativeai as genai
from models import SearchRequest, AnalysisResponse, ValidateKeyRequest, ValidateKeyResponse, MatchResult, SpecificOpportunity, Company
from services.company_search import search_companies
from services.ai_generator import generate_ai_analysis, analyze_company_opportunities
from services.real_search import search_google_places, search_openstreetmap, search_web_companies, _extract_country, _extract_city
from services.serpapi_search import search_serpapi
from services.website_analyzer import fetch_website_content

app = FastAPI(title="B2B Lead Finder API", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/validate/google-places", response_model=ValidateKeyResponse)
async def validate_google_key(request: ValidateKeyRequest):
    try:
        url = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": request.api_key,
            "X-Goog-FieldMask": "places.displayName",
        }
        payload = {"textQuery": "coffee shop new york"}
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                return ValidateKeyResponse(valid=True, message="Google Places API key válida")
            elif resp.status_code in (401, 403):
                return ValidateKeyResponse(valid=False, message="API key inválida o sin permisos para Places API (New)")
            elif resp.status_code == 429:
                return ValidateKeyResponse(valid=True, message="Key válida pero excediste el límite de requests")
            else:
                return ValidateKeyResponse(valid=False, message=f"Error {resp.status_code}: {resp.text[:150]}")
    except httpx.TimeoutException:
        return ValidateKeyResponse(valid=False, message="Timeout al conectar con Google")
    except Exception as e:
        return ValidateKeyResponse(valid=False, message=f"Error: {str(e)}")


@app.post("/api/validate/serpapi", response_model=ValidateKeyResponse)
async def validate_serpapi_key(request: ValidateKeyRequest):
    try:
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google",
            "q": "test",
            "api_key": request.api_key,
            "num": 1,
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                if "error" in data:
                    return ValidateKeyResponse(valid=False, message=f"SerpAPI error: {data['error']}")
                return ValidateKeyResponse(valid=True, message="SerpAPI key válida")
            else:
                return ValidateKeyResponse(valid=False, message=f"Error {resp.status_code}")
    except Exception as e:
        return ValidateKeyResponse(valid=False, message=f"Error: {str(e)}")


@app.post("/api/validate/gemini", response_model=ValidateKeyResponse)
async def validate_gemini_key(request: ValidateKeyRequest):
    try:
        genai.configure(api_key=request.api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Say hello in one word")
        if response.text:
            return ValidateKeyResponse(valid=True, message="Gemini API key válida")
        return ValidateKeyResponse(valid=False, message="No se recibió respuesta de Gemini")
    except Exception as e:
        error_msg = str(e).lower()
        if "api_key" in error_msg or "invalid" in error_msg or "permission" in error_msg:
            return ValidateKeyResponse(valid=False, message="API key inválida o sin permisos para Gemini API")
        return ValidateKeyResponse(valid=False, message=f"Error: {str(e)}")


@app.post("/api/search", response_model=AnalysisResponse)
async def search_leads(request: SearchRequest):
    try:
        companies = await _search_companies(request)

        if request.manual_companies:
            manual = _parse_manual_companies(request.manual_companies, request.location)
            companies = manual + companies

        if not companies:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron empresas. Agrega una Google Places API Key o SerpAPI Key para mejores resultados.",
            )

        results = search_companies(
            companies=companies,
            specialization=request.specialization,
            target_audience=request.target_audience,
            location=request.location,
        )

        if not results:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron empresas que coincidan con los criterios",
            )

        if request.deep_analysis and request.gemini_api_key:
            results = await _deep_analyze_companies(results, request)

        summary = _calculate_summary(results)
        use_cases = []

        if request.gemini_api_key:
            _, use_cases = generate_ai_analysis(
                specialization=request.specialization,
                target_audience=request.target_audience,
                location=request.location,
                results=results,
                api_key=request.gemini_api_key,
            )

        return AnalysisResponse(
            results=results,
            summary=summary,
            use_cases=use_cases,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _calculate_summary(results: list[MatchResult]) -> dict:
    alta = sum(1 for r in results if r.opportunity_level == "Alta")
    media = sum(1 for r in results if r.opportunity_level == "Media")
    baja = sum(1 for r in results if r.opportunity_level == "Baja")

    industries = {}
    for r in results:
        industries[r.company.industry] = industries.get(r.company.industry, 0) + 1
    top_industry = max(industries, key=industries.get) if industries else "N/A"

    return {
        "total_oportunidades": len(results),
        "alta_prioridad": alta,
        "media_prioridad": media,
        "baja_prioridad": baja,
        "industria_mas_prometedora": top_industry,
        "recomendacion_general": f"Enfócate en las {alta} empresas de alta prioridad. Prepara propuestas personalizadas para cada sector.",
    }


async def _search_companies(request: SearchRequest) -> list:
    all_companies = []

    if request.google_places_api_key:
        google_results = await search_google_places(
            target_audience=request.target_audience,
            location=request.location,
            api_key=request.google_places_api_key,
            max_results=20,
        )
        all_companies.extend(google_results)

    if not all_companies and request.serp_api_key:
        serp_results = await search_serpapi(
            target_audience=request.target_audience,
            location=request.location,
            api_key=request.serp_api_key,
            max_results=20,
        )
        all_companies.extend(serp_results)

    if not all_companies:
        web_results = await search_web_companies(
            target_audience=request.target_audience,
            location=request.location,
            max_results=20,
        )
        all_companies.extend(web_results)

    if not all_companies:
        osm_results = await search_openstreetmap(
            target_audience=request.target_audience,
            location=request.location,
            max_results=20,
        )
        all_companies.extend(osm_results)

    seen_names = set()
    unique_companies = []
    for c in all_companies:
        if c.name not in seen_names and len(c.name) > 3 and c.name != "Sin nombre":
            seen_names.add(c.name)
            unique_companies.append(c)

    return unique_companies


def _parse_manual_companies(manual_list: list[dict], location: str) -> list[Company]:
    companies = []
    for item in manual_list:
        company = Company(
            id=random.randint(1000, 9999),
            name=item.get("name", "Sin nombre"),
            industry=item.get("industry", "General"),
            size=item.get("size", "Desconocido"),
            employees=item.get("employees", 0),
            location=item.get("location", location),
            country=_extract_country(item.get("location", location)),
            city=_extract_city(item.get("location", location)),
            description=item.get("description", ""),
            website=item.get("website", "N/A"),
            pain_points=item.get("pain_points", []),
            budget_range=item.get("budget_range", "medio"),
            decision_makers=item.get("decision_makers", ["Gerente"]),
            growth_stage=item.get("growth_stage", "estable"),
            source="Manual",
            rating=0,
        )
        companies.append(company)
    return companies


async def _deep_analyze_companies(
    results: list[MatchResult],
    request: SearchRequest,
) -> list[MatchResult]:
    analyzed = []
    max_analyze = min(len(results), 10)

    for i, result in enumerate(results[:max_analyze]):
        if result.company.website and result.company.website != "N/A":
            content = await fetch_website_content(result.company.website)
            if content:
                result.company.website_content = content

        opportunities, ai_analysis = await analyze_company_opportunities(
            company=result,
            specialization=request.specialization,
            api_key=request.gemini_api_key,
        )

        result.specific_opportunities = opportunities
        result.ai_analysis = ai_analysis

        if opportunities:
            pain_points_from_opp = [
                f"Necesita: {opp.title}" for opp in opportunities
            ]
            result.company.pain_points = pain_points_from_opp

            high_impact = sum(1 for o in opportunities if o.impact == "alto")
            result.match_score = min(result.match_score + (high_impact * 10), 100)
            result.probability = min(result.probability + (high_impact * 8), 95)

            if result.match_score >= 70:
                result.opportunity_level = "Alta"
            elif result.match_score >= 45:
                result.opportunity_level = "Media"

        analyzed.append(result)

    results[max_analyze:] = [r for r in results[max_analyze:]]
    results.sort(key=lambda x: x.match_score, reverse=True)

    return results
