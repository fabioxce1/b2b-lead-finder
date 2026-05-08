import { useState } from "react";
import SearchForm from "./components/SearchForm";
import ResultsTable from "./components/ResultsTable";
import AnalysisPanel from "./components/AnalysisPanel";
import UseCases from "./components/UseCases";
import { searchLeads } from "./services/api";
import "./App.css";

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (formData) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const data = await searchLeads(formData);
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>B2B Lead Finder</h1>
        <p>Encuentra empresas ideales para ofrecer tus servicios</p>
      </header>

      <main className="app-main">
        <SearchForm onSearch={handleSearch} loading={loading} />

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner" />
            <p>Analizando oportunidades...</p>
          </div>
        )}

        {results && (
          <div className="results-container">
            <AnalysisPanel summary={results.summary} />
            <ResultsTable results={results.results} />
            <UseCases useCases={results.use_cases} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
