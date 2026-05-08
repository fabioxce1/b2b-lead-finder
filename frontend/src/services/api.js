const API_BASE = "http://localhost:8000";

export async function searchLeads(data) {
  const response = await fetch(`${API_BASE}/api/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Error en la búsqueda");
  }

  return response.json();
}

export async function validateGoogleKey(apiKey) {
  const response = await fetch(`${API_BASE}/api/validate/google-places`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: apiKey }),
  });
  return response.json();
}

export async function validateSerpAPIKey(apiKey) {
  const response = await fetch(`${API_BASE}/api/validate/serpapi`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: apiKey }),
  });
  return response.json();
}

export async function validateGeminiKey(apiKey) {
  const response = await fetch(`${API_BASE}/api/validate/gemini`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: apiKey }),
  });
  return response.json();
}
