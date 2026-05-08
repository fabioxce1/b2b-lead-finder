# B2B Lead Finder

Application to find real companies (potential clients) based on your specialization, target audience, and location. Searches the internet, analyzes company websites, and generates specific opportunities tailored to your services.

## Features

- Real-time internet search for companies (Google Places, SerpAPI, Web Search, OpenStreetMap)
- **Deep Analysis Mode**: Scrapes company websites and uses AI to identify specific opportunities for your specialization
- Smart matching algorithm that calculates conversion probability
- Manual company entry for known prospects
- Generated use cases with AI (Gemini)
- Modern and responsive interface

## How It Works

1. **Search**: Finds real companies matching your target audience in your specified location
2. **Match**: Calculates how well each company aligns with your specialization
3. **Deep Analysis** (optional): Visits each company's website and uses AI to identify concrete opportunities (automations, security improvements, system upgrades, etc.)
4. **Results**: Shows ranked companies with specific opportunities you can offer

## Requirements

- Python 3.10+
- Node.js 18+

## Installation

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Usage

1. Open http://localhost:5173 in your browser
2. Enter your **specialization** (e.g., "ingeniero de sistemas", "desarrollador web")
3. Define your **target audience** (e.g., "clínicas odontológicas", "empresas de desarrollo web")
4. Specify the **location** (e.g., "Bucaramanga", "Colombia", "Bogotá")
5. (Optional) Add your API keys for better results
6. Enable **Deep Analysis** to get specific opportunities per company
7. (Optional) Add companies manually if you already know them
8. Click "Buscar Empresas"

## API Keys

| Key | Purpose | Free Tier | How to get |
|-----|---------|-----------|------------|
| **Google Places API Key** | Best company search from Google | 200 requests/month | [Google Cloud Console](https://console.cloud.google.com/apis/library/places-backend.googleapis.com) |
| **SerpAPI Key** | Google search results programmatically | 100 searches/month | [serpapi.com](https://serpapi.com/users/sign_up) |
| **Gemini API Key** | AI analysis and opportunity generation | 15 RPM free | [aistudio.google.com](https://aistudio.google.com/apikey) |

All keys are optional. Without them, the app uses free alternatives (DuckDuckGo + OpenStreetMap for search, rule-based analysis instead of AI).

## Project Structure

```
b2b-lead-finder/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── models.py            # Pydantic models
│   ├── services/
│   │   ├── company_search.py  # Search and matching logic
│   │   ├── ai_generator.py    # AI analysis generation
│   │   ├── real_search.py     # Google Places + OSM search
│   │   ├── serpapi_search.py  # SerpAPI Google search
│   │   └── website_analyzer.py # Website scraping and analysis
│   └── requirements.txt
└── frontend/
    └── src/
        ├── App.jsx
        ├── components/
        │   ├── SearchForm.jsx
        │   ├── ResultsTable.jsx
        │   ├── AnalysisPanel.jsx
        │   └── UseCases.jsx
        └── services/
            └── api.js
```

## Matching Algorithm

The score is calculated based on:
- **Industry** (30 pts): Match between your specialization and the company's industry
- **Pain Points** (15 pts): Relationship between your service and their needs
- **Size** (15 pts): Match with your target audience
- **Location** (25 pts): Geographic proximity
- **Growth Stage** (5-10 pts): Companies in expansion have higher investment probability
- **Budget** (5-10 pts): Investment capacity
- **Deep Analysis** (+10 pts per high-impact opportunity found)
