from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import SearchRequest, AnalysisResponse
from services.company_search import search_companies
from services.ai_generator import generate_ai_analysis

app = FastAPI(title="B2B Lead Finder API", version="1.0.0")

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


@app.post("/api/search", response_model=AnalysisResponse)
def search_leads(request: SearchRequest):
    try:
        results = search_companies(
            specialization=request.specialization,
            target_audience=request.target_audience,
            location=request.location,
        )

        if not results:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron empresas que coincidan con los criterios",
            )

        summary, use_cases = generate_ai_analysis(
            specialization=request.specialization,
            target_audience=request.target_audience,
            location=request.location,
            results=results,
            api_key=request.openai_api_key,
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
