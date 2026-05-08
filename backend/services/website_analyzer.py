import httpx
import re
from typing import Optional
from bs4 import BeautifulSoup


async def fetch_website_content(url: str, max_chars: int = 5000) -> Optional[str]:
    if not url or url == "N/A":
        return None

    if not url.startswith("http"):
        url = "https://" + url

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es,en;q=0.5",
    }

    try:
        async with httpx.AsyncClient(
            timeout=15, follow_redirects=True, verify=False
        ) as client:
            response = await client.get(url, headers=headers)

            if response.status_code != 200:
                return None

            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            for tag in soup(["script", "style", "nav", "footer", "header", "iframe"]):
                tag.decompose()

            text = soup.get_text(separator=" ", strip=True)
            text = re.sub(r"\s+", " ", text)
            text = re.sub(r"[^\w\s.,;:!?()-]", "", text)

            if len(text) > max_chars:
                text = text[:max_chars]

            return text.strip()

    except Exception:
        return None


def extract_business_info(content: str) -> dict:
    if not content:
        return {}

    content_lower = content.lower()

    services = []
    service_keywords = [
        "servicio", "tratamiento", "procedimiento", "consulta",
        "cirugía", "cirugia", "diagnóstico", "diagnostico",
        "emergencia", "urgencia", "programa", "plan",
    ]

    sentences = re.split(r"[.!?]+", content)
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 20 and len(sentence) < 200:
            for keyword in service_keywords:
                if keyword in sentence.lower():
                    services.append(sentence.strip())
                    break

    tech_indicators = []
    tech_keywords = [
        "online", "digital", "app", "sistema", "software",
        "plataforma", "portal", "web", "internet", "tecnología",
        "tecnologia", "automatización", "automatizacion",
    ]

    for keyword in tech_keywords:
        if keyword in content_lower:
            tech_indicators.append(keyword)

    return {
        "services": services[:10],
        "tech_level": len(tech_indicators),
        "tech_indicators": tech_indicators,
        "content_length": len(content),
    }
