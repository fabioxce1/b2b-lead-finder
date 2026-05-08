import httpx
import random
import re
from typing import Optional
from models import Company
from services.real_search import _detect_industry, _extract_country, _extract_city


async def search_serpapi(
    target_audience: str,
    location: str,
    api_key: str,
    max_results: int = 20,
) -> list[Company]:
    search_queries = [
        f"empresas de {target_audience} en {location}",
        f"{target_audience} {location} servicios",
        f"{target_audience} {location} colombia",
    ]

    companies = []
    seen_urls = set()

    for query in search_queries:
        if len(companies) >= max_results:
            break

        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "hl": "es",
            "gl": "co",
            "num": 10,
        }

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    organic_results = data.get("organic_results", [])

                    for result in organic_results:
                        link = result.get("link", "")
                        title = result.get("title", "")
                        snippet = result.get("snippet", "")

                        if not link or link in seen_urls:
                            continue

                        if _is_skip_url(link):
                            continue

                        seen_urls.add(link)

                        if len(companies) >= max_results:
                            break

                        company_name = _extract_company_from_result(title, snippet, target_audience)

                        if not company_name or len(company_name) < 3:
                            continue

                        detected_industry = _detect_industry([target_audience, title, snippet, company_name])

                        company = Company(
                            id=random.randint(1000, 9999),
                            name=company_name,
                            industry=detected_industry,
                            size="Desconocido",
                            employees=0,
                            location=location,
                            country=_extract_country(location),
                            city=_extract_city(location),
                            description=snippet[:300],
                            website=link,
                            pain_points=[],
                            budget_range="medio",
                            decision_makers=["Gerente"],
                            growth_stage="estable",
                            source="SerpAPI",
                            rating=0,
                        )
                        companies.append(company)

        except Exception as e:
            print(f"Error SerpAPI: {e}")

    return companies


def _is_skip_url(url: str) -> bool:
    url_lower = url.lower()
    skip_domains = [
        "youtube.com", "facebook.com", "twitter.com", "instagram.com",
        "tiktok.com", "pinterest.com", "linkedin.com/company",
        "wikipedia.org", "tripadvisor.", "yelp.", "foursquare.",
        "duckduckgo.com", "google.com/search", "google.com/maps",
        "maps.google.", "waze.com",
    ]
    return any(domain in url_lower for domain in skip_domains)


def _extract_company_from_result(title: str, snippet: str, target_audience: str) -> str:
    title_clean = re.sub(r'\s*[-–—]\s*.*$', '', title)
    title_clean = re.sub(r'\s*\|.*$', '', title_clean)
    title_clean = re.sub(r'\s*–.*$', '', title_clean)
    title_clean = title_clean.strip()

    skip_words = ["top", "best", "list", "ranking", "2026", "2025", "the", "a", "an", "mejores", "las", "los", "empresas", "de", "en", "guía", "guia"]
    words = title_clean.split()

    if words and words[0].lower() not in skip_words and len(words) <= 5:
        return title_clean

    mentions = re.findall(r'"([^"]+)"', snippet)
    if mentions:
        return mentions[0]

    target_words = target_audience.lower().split()
    title_lower = title_clean.lower()

    for tw in target_words:
        idx = title_lower.find(tw)
        if idx > 0:
            candidate = title_clean[:idx].strip()
            candidate = re.sub(r'\s*[-–—]\s*.*$', '', candidate)
            if len(candidate) > 2:
                return candidate

    return title_clean[:60] if title_clean else "Empresa"
