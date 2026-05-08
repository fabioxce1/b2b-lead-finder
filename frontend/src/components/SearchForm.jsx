import { useState } from "react";
import { validateGoogleKey, validateSerpAPIKey, validateGeminiKey } from "../services/api";

export default function SearchForm({ onSearch, loading }) {
  const [form, setForm] = useState({
    specialization: "",
    target_audience: "",
    location: "",
    google_places_api_key: "",
    serp_api_key: "",
    gemini_api_key: "",
    deep_analysis: false,
    manual_companies: [],
  });

  const [keyStatus, setKeyStatus] = useState({
    google: null,
    serp: null,
    gemini: null,
  });

  const [keyMessages, setKeyMessages] = useState({
    google: "",
    serp: "",
    gemini: "",
  });

  const [keyTouched, setKeyTouched] = useState({
    google: false,
    serp: false,
    gemini: false,
  });

  const [showManualForm, setShowManualForm] = useState(false);
  const [manualCompany, setManualCompany] = useState({
    name: "",
    website: "",
    description: "",
    industry: "",
  });

  const handleValidate = async (keyType) => {
    const keyMap = {
      google: form.google_places_api_key,
      serp: form.serp_api_key,
      gemini: form.gemini_api_key,
    };
    const key = keyMap[keyType];
    if (!key) return;

    setKeyStatus({ ...keyStatus, [keyType]: "validating" });
    setKeyMessages({ ...keyMessages, [keyType]: "Validando..." });

    const validateFn = {
      google: validateGoogleKey,
      serp: validateSerpAPIKey,
      gemini: validateGeminiKey,
    }[keyType];

    const result = await validateFn(key);

    setKeyStatus({ ...keyStatus, [keyType]: result.valid ? "valid" : "invalid" });
    setKeyMessages({ ...keyMessages, [keyType]: result.message });
  };

  const handleBlur = (keyType) => {
    const keyMap = {
      google: form.google_places_api_key,
      serp: form.serp_api_key,
      gemini: form.gemini_api_key,
    };
    const key = keyMap[keyType];
    if (key && keyTouched[keyType]) {
      handleValidate(keyType);
    }
    setKeyTouched({ ...keyTouched, [keyType]: true });
  };

  const handleChange = (field, value) => {
    if (["google_places_api_key", "serp_api_key", "gemini_api_key"].includes(field)) {
      const keyType = field === "google_places_api_key" ? "google" : field === "serp_api_key" ? "serp" : "gemini";
      setKeyStatus({ ...keyStatus, [keyType]: null });
      setKeyMessages({ ...keyMessages, [keyType]: "" });
    }
    setForm({ ...form, [field]: value });
  };

  const addManualCompany = () => {
    if (manualCompany.name && manualCompany.website) {
      setForm({
        ...form,
        manual_companies: [...form.manual_companies, { ...manualCompany }],
      });
      setManualCompany({ name: "", website: "", description: "", industry: "" });
    }
  };

  const removeManualCompany = (index) => {
    setForm({
      ...form,
      manual_companies: form.manual_companies.filter((_, i) => i !== index),
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (form.specialization && form.target_audience && form.location) {
      onSearch(form);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="search-form">
      <h2>Configura tu búsqueda</h2>

      <div className="form-group">
        <label htmlFor="specialization">Tu especialización / servicio que ofreces</label>
        <input
          id="specialization"
          type="text"
          placeholder="Ej: Ingeniero de sistemas, marketing digital..."
          value={form.specialization}
          onChange={(e) => handleChange("specialization", e.target.value)}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="target_audience">Público objetivo (tipo de empresa)</label>
        <input
          id="target_audience"
          type="text"
          placeholder="Ej: Clínicas odontológicas, empresas de desarrollo web..."
          value={form.target_audience}
          onChange={(e) => handleChange("target_audience", e.target.value)}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="location">Ubicación</label>
        <input
          id="location"
          type="text"
          placeholder="Ej: Bucaramanga, Colombia, Bogotá..."
          value={form.location}
          onChange={(e) => handleChange("location", e.target.value)}
          required
        />
      </div>

      <div className="form-group">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={form.deep_analysis}
            onChange={(e) => handleChange("deep_analysis", e.target.checked)}
          />
          <span>Análisis profundo con IA</span>
        </label>
        {!form.gemini_api_key && form.deep_analysis && (
          <p className="field-hint field-warning">Requiere Gemini API Key para funcionar</p>
        )}
        {form.gemini_api_key && form.deep_analysis && (
          <p className="field-hint">Analiza el sitio web de cada empresa y genera oportunidades específicas</p>
        )}
        {!form.deep_analysis && (
          <p className="field-hint">Analiza el sitio web de cada empresa y genera oportunidades específicas para tu especialización</p>
        )}
      </div>

      <div className="api-keys-section">
        <h3>API Keys (opcional, para mejores resultados)</h3>

        <div className="api-key-row">
          <div className="form-group">
            <label htmlFor="google_places_api_key">Google Places API Key</label>
            <div className="key-input-wrapper">
              <input
                id="google_places_api_key"
                type="password"
                placeholder="AIza..."
                value={form.google_places_api_key}
                onChange={(e) => handleChange("google_places_api_key", e.target.value)}
                onBlur={() => handleBlur("google")}
              />
              <button
                type="button"
                className="validate-btn"
                disabled={!form.google_places_api_key || keyStatus.google === "validating"}
                onClick={() => handleValidate("google")}
              >
                {keyStatus.google === "validating" ? "..." : "Validar"}
              </button>
            </div>
            {keyStatus.google && (
              <div className={`key-status ${keyStatus.google}`}>
                {keyStatus.google === "validating" && <div className="mini-spinner" />}
                {keyStatus.google === "valid" && <span className="status-icon">✓</span>}
                {keyStatus.google === "invalid" && <span className="status-icon">✗</span>}
                <span>{keyMessages.google}</span>
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="serp_api_key">SerpAPI Key</label>
            <div className="key-input-wrapper">
              <input
                id="serp_api_key"
                type="password"
                placeholder="Tu key de serpapi.com"
                value={form.serp_api_key}
                onChange={(e) => handleChange("serp_api_key", e.target.value)}
                onBlur={() => handleBlur("serp")}
              />
              <button
                type="button"
                className="validate-btn"
                disabled={!form.serp_api_key || keyStatus.serp === "validating"}
                onClick={() => handleValidate("serp")}
              >
                {keyStatus.serp === "validating" ? "..." : "Validar"}
              </button>
            </div>
            {keyStatus.serp && (
              <div className={`key-status ${keyStatus.serp}`}>
                {keyStatus.serp === "validating" && <div className="mini-spinner" />}
                {keyStatus.serp === "valid" && <span className="status-icon">✓</span>}
                {keyStatus.serp === "invalid" && <span className="status-icon">✗</span>}
                <span>{keyMessages.serp}</span>
              </div>
            )}
          </div>
        </div>

        <div className="api-key-row">
          <div className="form-group">
            <label htmlFor="gemini_api_key">Gemini API Key</label>
            <div className="key-input-wrapper">
              <input
                id="gemini_api_key"
                type="password"
                placeholder="AIza..."
                value={form.gemini_api_key}
                onChange={(e) => handleChange("gemini_api_key", e.target.value)}
                onBlur={() => handleBlur("gemini")}
              />
              <button
                type="button"
                className="validate-btn"
                disabled={!form.gemini_api_key || keyStatus.gemini === "validating"}
                onClick={() => handleValidate("gemini")}
              >
                {keyStatus.gemini === "validating" ? "..." : "Validar"}
              </button>
            </div>
            {keyStatus.gemini && (
              <div className={`key-status ${keyStatus.gemini}`}>
                {keyStatus.gemini === "validating" && <div className="mini-spinner" />}
                {keyStatus.gemini === "valid" && <span className="status-icon">✓</span>}
                {keyStatus.gemini === "invalid" && <span className="status-icon">✗</span>}
                <span>{keyMessages.gemini}</span>
              </div>
            )}
          </div>
        </div>

        <p className="api-hints">
          <a href="https://console.cloud.google.com/apis/library/places-backend.googleapis.com" target="_blank" rel="noopener">Obtener Google Places API Key</a> · {" "}
          <a href="https://serpapi.com/users/sign_up" target="_blank" rel="noopener">Obtener SerpAPI Key (100 gratis/mes)</a> · {" "}
          <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener">Obtener Gemini API Key (gratis)</a>
        </p>
      </div>

      <div className="manual-section">
        <button
          type="button"
          className="toggle-manual-btn"
          onClick={() => setShowManualForm(!showManualForm)}
        >
          {showManualForm ? "− Ocultar" : "+ Agregar empresa manualmente"}
        </button>

        {showManualForm && (
          <div className="manual-form">
            <div className="manual-inputs">
              <input
                type="text"
                placeholder="Nombre de la empresa"
                value={manualCompany.name}
                onChange={(e) => setManualCompany({ ...manualCompany, name: e.target.value })}
              />
              <input
                type="text"
                placeholder="Sitio web (ej: damos.co)"
                value={manualCompany.website}
                onChange={(e) => setManualCompany({ ...manualCompany, website: e.target.value })}
              />
              <input
                type="text"
                placeholder="Industria (ej: Tecnología)"
                value={manualCompany.industry}
                onChange={(e) => setManualCompany({ ...manualCompany, industry: e.target.value })}
              />
              <input
                type="text"
                placeholder="Descripción breve"
                value={manualCompany.description}
                onChange={(e) => setManualCompany({ ...manualCompany, description: e.target.value })}
              />
              <button type="button" className="add-company-btn" onClick={addManualCompany}>
                Agregar
              </button>
            </div>

            {form.manual_companies.length > 0 && (
              <div className="manual-list">
                {form.manual_companies.map((mc, i) => (
                  <div key={i} className="manual-item">
                    <span>{mc.name} — {mc.website}</span>
                    <button type="button" className="remove-btn" onClick={() => removeManualCompany(i)}>×</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <button type="submit" disabled={loading} className="btn-primary">
        {loading ? "Buscando..." : "Buscar Empresas"}
      </button>
    </form>
  );
}
