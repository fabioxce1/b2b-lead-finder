import httpx
import random
import re
import json
from typing import Optional
from models import Company

INDUSTRY_KEYWORDS = {
    "Tecnología": ["software", "technology", "tech", "IT", "digital", "cloud", "computing", "app", "development", "programación", "desarrollo", "desarrollo web", "sistemas", "ingeniería de sistemas"],
    "Marketing": ["marketing", "advertising", "digital agency", "branding", "media", "publicidad", "SEO", "SEM", "social media"],
    "Salud": ["health", "medical", "clinic", "hospital", "healthcare", "pharma", "salud", "clínica", "doctor", "odontología", "odontologia", "dental", "dentista"],
    "Educación": ["education", "academy", "school", "university", "training", "learning", "educación", "coaching", "curso", "colegio", "instituto"],
    "Construcción": ["construction", "building", "engineering", "real estate", "developer", "constructora", "arquitectura", "architect"],
    "Retail": ["retail", "store", "shop", "fashion", "clothing", "commerce", "e-commerce", "tienda", "moda"],
    "Agricultura": ["agriculture", "farm", "agro", "food production", "organic", "agrícola"],
    "Finanzas": ["finance", "bank", "fintech", "insurance", "investment", "accounting", "finanzas", "contabilidad", "banco"],
    "Logística": ["logistics", "transport", "shipping", "delivery", "freight", "cargo", "logística", "transporte"],
    "Entretenimiento": ["entertainment", "media", "production", "studio", "gaming", "entretenimiento"],
    "Energía": ["energy", "solar", "renewable", "power", "electric", "energía", "renovable"],
    "Automotriz": ["automotive", "auto", "car", "vehicle", "parts", "motor", "automotriz"],
    "Turismo": ["tourism", "hotel", "travel", "resort", "hospitality", "tour", "turismo", "viajes", "hotel"],
    "Farmacéutica": ["pharmaceutical", "pharma", "biotech", "laboratory", "medical research", "farmacéutica"],
    "Legal": ["law", "legal", "attorney", "law firm", "advisory", "abogados", "abogacía", "notaría"],
    "Consultoría": ["consulting", "consultancy", "advisory", "strategy", "consultoría", "asesoría"],
    "Alimentos": ["food", "restaurant", "beverage", "nutrition", "organic food", "alimentos", "restaurante"],
}

OSM_AMENITY_MAP = {
    "desarrollo": ["it", "company", "telecommunication"],
    "software": ["it", "company", "telecommunication"],
    "tecnología": ["it", "company", "telecommunication"],
    "tecnologia": ["it", "company", "telecommunication"],
    "web": ["it", "company", "telecommunication"],
    "sistemas": ["it", "company", "telecommunication"],
    "clínica": ["clinic", "doctors", "dentist", "hospital"],
    "odontología": ["dentist", "clinic", "doctors"],
    "odontologia": ["dentist", "clinic", "doctors"],
    "dental": ["dentist", "clinic", "doctors"],
    "salud": ["clinic", "doctors", "hospital", "dentist"],
    "restaurante": ["restaurant", "cafe", "fast_food", "food_court"],
    "colegio": ["school", "university", "college"],
    "educación": ["school", "university", "college", "training"],
    "educacion": ["school", "university", "college", "training"],
    "abogado": ["lawyer", "notary"],
    "legal": ["lawyer", "notary"],
    "finanzas": ["bank", "accountant", "financial"],
    "contabilidad": ["accountant", "financial"],
    "marketing": ["advertising_agency", "company"],
    "publicidad": ["advertising_agency", "company"],
    "consultoría": ["company", "financial", "lawyer"],
    "consultoria": ["company", "financial", "lawyer"],
    "hotel": ["hotel", "motel", "guest_house", "hostel"],
    "turismo": ["travel_agent", "hotel"],
    "viajes": ["travel_agent", "hotel"],
    "empresa": ["company"],
    "agencia": ["company", "advertising_agency"],
    "estudio": ["company"],
}

LISTICLE_PATTERNS = [
    r"top\s+\d+",
    r"las?\s+\d+\s+mejores",
    r"los?\s+\d+\s+mejores",
    r"\d+\s+(empresas|agencias|estudios|clínicas|restaurantes)",
    r"(ranking|lista|list)\s+(de\s+)?\d+",
    r"mejores\s+\d+",
]

SKIP_DOMAINS = [
    "duckduckgo.com", "google.com/search", "youtube.com", "facebook.com",
    "twitter.com", "instagram.com", "linkedin.com/company", "wikipedia.org",
    "tripadvisor.", "yelp.", "foursquare.", "pinterest.", "tiktok.com",
]


async def geocode_location(location: str) -> Optional[dict]:
    geocode_url = "https://nominatim.openstreetmap.org/search"
    geocode_params = {
        "q": location,
        "format": "json",
        "limit": 1,
    }
    headers = {"User-Agent": "B2BLeadFinder/1.0"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(geocode_url, params=geocode_params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data:
                    return {
                        "lat": float(data[0]["lat"]),
                        "lon": float(data[0]["lon"]),
                        "display_name": data[0]["display_name"],
                    }
    except Exception as e:
        print(f"Error geocoding: {e}")

    return None


async def search_google_places(
    target_audience: str,
    location: str,
    api_key: str,
    max_results: int = 20,
) -> list[Company]:
    search_query = f"{target_audience} {location}"

    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.internationalPhoneNumber,places.websiteUri,places.types,places.rating,places.userRatingCount,places.businessStatus,places.editorialSummary",
    }

    payload = {
        "textQuery": search_query,
        "languageCode": "es",
    }

    companies = []

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                places = data.get("places", [])

                for place in places[:max_results]:
                    name = place.get("displayName", {}).get("text", "Unknown")
                    address = place.get("formattedAddress", "")
                    website = place.get("websiteUri", "")
                    phone = place.get("internationalPhoneNumber", "")
                    place_types = place.get("types", [])
                    rating = place.get("rating", 0)
                    summary = place.get("editorialSummary", {}).get("text", "")

                    detected_industry = _detect_industry(place_types + [target_audience, name, summary])

                    company = Company(
                        id=random.randint(1000, 9999),
                        name=name,
                        industry=detected_industry,
                        size="Desconocido",
                        employees=0,
                        location=address,
                        country=_extract_country(address),
                        city=_extract_city(address),
                        description=summary or f"Empresa de {detected_industry} en {address}",
                        website=website or "N/A",
                        pain_points=[],
                        budget_range="medio",
                        decision_makers=["Gerente"],
                        growth_stage="estable",
                        source="Google Places",
                        rating=rating,
                    )
                    companies.append(company)

    except Exception as e:
        print(f"Error en Google Places: {e}")

    return companies


async def search_openstreetmap(
    target_audience: str,
    location: str,
    max_results: int = 20,
) -> list[Company]:
    geo = await geocode_location(location)
    if not geo:
        return []

    lat = geo["lat"]
    lon = geo["lon"]
    display_name = geo["display_name"]

    amenity_types = _get_osm_amenity_types(target_audience)

    queries = []
    for amenity in amenity_types:
        queries.append(f'nwr["office"="{amenity}"](around:20000, {lat}, {lon});')

    if not queries:
        queries.append(f'nwr["office"="it"](around:20000, {lat}, {lon});')
        queries.append(f'nwr["office"="company"](around:20000, {lat}, {lon});')
        queries.append(f'nwr["office"="telecommunication"](around:20000, {lat}, {lon});')

    overpass_query = f"""
    [out:json][timeout:30];
    ({' '.join(queries)});
    out center {max_results * 3};
    """

    overpass_url = "https://overpass-api.de/api/interpreter"
    companies = []

    headers = {"User-Agent": "B2BLeadFinder/1.0"}
    target_lower = target_audience.lower()

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                overpass_url,
                data={"data": overpass_query},
                headers=headers,
            )

            if response.status_code == 200:
                data = response.json()
                elements = data.get("elements", [])

                for elem in elements[:max_results * 3]:
                    tags = elem.get("tags", {})
                    name = tags.get("name", "")
                    amenity = tags.get("office", tags.get("amenity", tags.get("shop", "")))
                    website = tags.get("website", tags.get("contact:website", ""))
                    description = tags.get("description", "")

                    if not name or len(name) < 3:
                        continue

                    combined_text = f"{name} {description} {amenity}".lower()
                    is_relevant = any(
                        kw in combined_text for kw in target_lower.split()
                    )
                    if not is_relevant:
                        continue

                    detected_industry = _detect_industry([amenity, target_audience, name, description])

                    company = Company(
                        id=random.randint(1000, 9999),
                        name=name,
                        industry=detected_industry,
                        size="Desconocido",
                        employees=0,
                        location=display_name,
                        country=_extract_country(display_name),
                        city=_extract_city(display_name),
                        description=description or f"{detected_industry} - {amenity}",
                        website=website or "N/A",
                        pain_points=[],
                        budget_range="medio",
                        decision_makers=["Gerente"],
                        growth_stage="estable",
                        source="OpenStreetMap",
                        rating=0,
                    )
                    companies.append(company)

    except Exception as e:
        print(f"Error OpenStreetMap: {e}")

    return companies


async def search_web_companies(
    target_audience: str,
    location: str,
    max_results: int = 20,
) -> list[Company]:
    search_queries = [
        f'empresas de {target_audience} en {location}',
        f'{target_audience} {location} empresa servicios',
        f'{target_audience} {location} "contáctenos" OR "contacto"',
        f'{target_audience} {location} colombia',
        f'"{target_audience}" {location} sitio oficial',
    ]

    companies = []
    seen_urls = set()

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es,en;q=0.5",
    }

    for query in search_queries:
        if len(companies) >= max_results:
            break

        url = "https://html.duckduckgo.com/html/"
        params = {"q": query}

        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                response = await client.get(url, params=params, headers=headers)

                if response.status_code == 200:
                    html = response.text
                    results = _parse_duckduckgo_results(html)

                    for result in results:
                        if result["url"] in seen_urls:
                            continue

                        if _is_skip_domain(result["url"]):
                            continue

                        if _is_listicle(result["title"], result["snippet"]):
                            continue

                        seen_urls.add(result["url"])

                        if len(companies) >= max_results:
                            break

                        company_name = _extract_company_name(result["title"], result["snippet"], target_audience)

                        if not company_name or len(company_name) < 3:
                            continue

                        detected_industry = _detect_industry([target_audience, result["title"], result["snippet"], company_name])

                        company = Company(
                            id=random.randint(1000, 9999),
                            name=company_name,
                            industry=detected_industry,
                            size="Desconocido",
                            employees=0,
                            location=location,
                            country=_extract_country(location),
                            city=_extract_city(location),
                            description=result["snippet"][:300],
                            website=result["url"],
                            pain_points=[],
                            budget_range="medio",
                            decision_makers=["Gerente"],
                            growth_stage="estable",
                            source="Web Search",
                            rating=0,
                        )
                        companies.append(company)

        except Exception as e:
            print(f"Error web search: {e}")

    return companies


def _is_skip_domain(url: str) -> bool:
    url_lower = url.lower()
    return any(domain in url_lower for domain in SKIP_DOMAINS)


def _is_listicle(title: str, snippet: str) -> bool:
    combined = f"{title} {snippet}".lower()
    for pattern in LISTICLE_PATTERNS:
        if re.search(pattern, combined):
            return True
    return False


def _detect_industry(keywords: list[str]) -> str:
    text = " ".join(keywords).lower()

    for industry, keywords_list in INDUSTRY_KEYWORDS.items():
        if any(kw in text for kw in keywords_list):
            return industry

    return "General"


def _get_osm_amenity_types(target_audience: str) -> list[str]:
    target_lower = target_audience.lower()
    matched_types = []

    for keyword, amenity_types in OSM_AMENITY_MAP.items():
        if keyword in target_lower:
            matched_types.extend(amenity_types)

    return list(set(matched_types))


def _extract_country(address: str) -> str:
    parts = address.split(",")
    return parts[-1].strip() if parts else "Desconocido"


def _extract_city(address: str) -> str:
    parts = address.split(",")
    return parts[0].strip() if len(parts) > 0 else "Desconocido"


def _parse_duckduckgo_results(html: str) -> list[dict]:
    results = []

    title_pattern = re.compile(r'class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>')
    snippet_pattern = re.compile(r'class="result__snippet"[^>]*>(.*?)</span>', re.DOTALL)

    titles = title_pattern.findall(html)
    snippets = snippet_pattern.findall(html)

    for i, (url, title) in enumerate(titles):
        clean_title = re.sub(r"<[^>]+>", "", title).strip()
        clean_snippet = re.sub(r"<[^>]+>", "", snippets[i]).strip() if i < len(snippets) else ""

        if clean_title and clean_snippet:
            results.append({
                "title": clean_title,
                "url": url,
                "snippet": clean_snippet[:300],
            })

    return results


def _extract_company_name(title: str, snippet: str, target_audience: str) -> str:
    title_clean = re.sub(r'\s*[-–—]\s*.*$', '', title)
    title_clean = re.sub(r'\s*\|.*$', '', title_clean)
    title_clean = re.sub(r'\s*–.*$', '', title_clean)
    title_clean = title_clean.strip()

    skip_words = ["top", "best", "list", "ranking", "2026", "2025", "the", "a", "an", "in", "of", "and", "mejores", "las", "los", "empresas", "de", "en"]
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
