# B2B Lead Finder

Aplicación para buscar empresas (clientes potenciales) basándose en tu especialización, público objetivo y ubicación. Genera un análisis completo con probabilidades, oportunidades y casos de uso puntuales.

## Características

- Búsqueda inteligente de empresas por especialización, público objetivo y ubicación
- Algoritmo de matching que calcula probabilidad de conversión
- Análisis general con estadísticas de oportunidades
- Casos de uso puntuales generados (con IA opcional)
- Base de datos de 20+ empresas de ejemplo en Latinoamérica
- Interfaz moderna y responsiva

## Requisitos

- Python 3.10+
- Node.js 18+

## Instalación

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Uso

1. Abre http://localhost:5173 en tu navegador
2. Ingresa tu especialización (ej: "marketing digital", "desarrollo web")
3. Define tu público objetivo (ej: "empresas medianas", "startups")
4. Especifica la ubicación (ej: "Colombia", "México", "Latinoamérica")
5. (Opcional) Agrega tu API key de OpenAI para análisis con IA
6. Haz clic en "Buscar Empresas"

## Estructura del Proyecto

```
b2b-lead-finder/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── models.py            # Pydantic models
│   ├── services/
│   │   ├── company_search.py  # Lógica de búsqueda y matching
│   │   └── ai_generator.py    # Generación de análisis con IA
│   ├── data/
│   │   └── sample_companies.json  # Base de datos de empresas
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

## Algoritmo de Matching

El score se calcula basándose en:
- **Industria** (30 pts): Coincidencia entre tu especialización y la industria
- **Pain Points** (15 pts): Relación entre tu servicio y las necesidades
- **Tamaño** (15 pts): Coincidencia con tu público objetivo
- **Ubicación** (25 pts): Proximidad geográfica
- **Etapa de crecimiento** (5-10 pts): Empresas en expansión tienen más probabilidad
- **Presupuesto** (5-10 pts): Capacidad de inversión

## Agregar más empresas

Edita `backend/data/sample_companies.json` siguiendo el formato existente.
