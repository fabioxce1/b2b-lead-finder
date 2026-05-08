# B2B Lead Finder

Application to find companies (potential clients) based on your specialization, target audience, and location. Generates a complete analysis with probabilities, opportunities, and specific use cases.

## Features

- Smart company search by specialization, target audience, and location
- Matching algorithm that calculates conversion probability
- General analysis with opportunity statistics
- Generated use cases (with optional AI)
- Database of 20+ sample companies across Latin America
- Modern and responsive interface

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
2. Enter your specialization (e.g., "digital marketing", "web development")
3. Define your target audience (e.g., "medium-sized companies", "startups")
4. Specify the location (e.g., "Colombia", "Mexico", "Latin America")
5. (Optional) Add your OpenAI API key for AI-powered analysis
6. Click "Buscar Empresas" (Search Companies)

## Project Structure

```
b2b-lead-finder/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── models.py            # Pydantic models
│   ├── services/
│   │   ├── company_search.py  # Search and matching logic
│   │   └── ai_generator.py    # AI analysis generation
│   ├── data/
│   │   └── sample_companies.json  # Company database
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

## Adding More Companies

Edit `backend/data/sample_companies.json` following the existing format.
