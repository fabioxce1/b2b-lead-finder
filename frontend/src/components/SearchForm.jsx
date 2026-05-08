import { useState } from "react";

export default function SearchForm({ onSearch, loading }) {
  const [form, setForm] = useState({
    specialization: "",
    target_audience: "",
    location: "",
    openai_api_key: "",
  });

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
          placeholder="Ej: Marketing digital, desarrollo web, consultoría TI..."
          value={form.specialization}
          onChange={(e) => setForm({ ...form, specialization: e.target.value })}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="target_audience">Público objetivo</label>
        <input
          id="target_audience"
          type="text"
          placeholder="Ej: Empresas medianas, startups, grandes corporaciones..."
          value={form.target_audience}
          onChange={(e) => setForm({ ...form, target_audience: e.target.value })}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="location">Ubicación</label>
        <input
          id="location"
          type="text"
          placeholder="Ej: Colombia, Bogotá, México, Latinoamérica..."
          value={form.location}
          onChange={(e) => setForm({ ...form, location: e.target.value })}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="api_key">
          OpenAI API Key <span>(opcional, para análisis con IA)</span>
        </label>
        <input
          id="api_key"
          type="password"
          placeholder="sk-..."
          value={form.openai_api_key}
          onChange={(e) => setForm({ ...form, openai_api_key: e.target.value })}
        />
      </div>

      <button type="submit" disabled={loading} className="btn-primary">
        {loading ? "Buscando..." : "Buscar Empresas"}
      </button>
    </form>
  );
}
