export default function AnalysisPanel({ summary }) {
  if (!summary) return null;

  return (
    <div className="analysis-section">
      <h2>Análisis General</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-number">{summary.total_oportunidades}</span>
          <span className="stat-label">Total Oportunidades</span>
        </div>
        <div className="stat-card stat-high">
          <span className="stat-number">{summary.alta_prioridad}</span>
          <span className="stat-label">Alta Prioridad</span>
        </div>
        <div className="stat-card stat-medium">
          <span className="stat-number">{summary.media_prioridad}</span>
          <span className="stat-label">Media Prioridad</span>
        </div>
        <div className="stat-card stat-low">
          <span className="stat-number">{summary.baja_prioridad}</span>
          <span className="stat-label">Baja Prioridad</span>
        </div>
      </div>

      <div className="insight-card">
        <h3>Industria más prometedora</h3>
        <p>{summary.industria_mas_prometedora}</p>
      </div>

      <div className="insight-card recommendation-card">
        <h3>Recomendación General</h3>
        <p>{summary.recomendacion_general}</p>
      </div>
    </div>
  );
}
