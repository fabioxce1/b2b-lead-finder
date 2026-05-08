import React, { useState } from "react";

export default function ResultsTable({ results }) {
  const [expandedId, setExpandedId] = useState(null);

  const getScoreColor = (score) => {
    if (score >= 70) return "#22c55e";
    if (score >= 45) return "#f59e0b";
    return "#ef4444";
  };

  const getOpportunityBadge = (level) => {
    const classes = {
      Alta: "badge-high",
      Media: "badge-medium",
      Baja: "badge-low",
    };
    return classes[level] || "badge-low";
  };

  const getImpactBadge = (impact) => {
    const classes = {
      alto: "impact-high",
      medio: "impact-medium",
      bajo: "impact-low",
    };
    return classes[impact] || "impact-low";
  };

  const getEffortBadge = (effort) => {
    const classes = {
      alto: "effort-high",
      medio: "effort-medium",
      bajo: "effort-low",
    };
    return classes[effort] || "effort-medium";
  };

  return (
    <div className="results-section">
      <h2>Resultados: {results.length} empresas encontradas</h2>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Empresa</th>
              <th>Industria</th>
              <th>Ubicación</th>
              <th>Fuente</th>
              <th>Match</th>
              <th>Probabilidad</th>
              <th>Oportunidad</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {results.map((result, index) => (
              <React.Fragment key={result.company.id}>
                <tr
                  className={expandedId === result.company.id ? "expanded" : ""}
                  onClick={() =>
                    setExpandedId(
                      expandedId === result.company.id ? null : result.company.id
                    )
                  }
                  style={{ cursor: "pointer" }}
                >
                  <td>{index + 1}</td>
                  <td className="company-name">
                    {result.company.name}
                    <span className="company-size">{result.company.size}</span>
                  </td>
                  <td>{result.company.industry}</td>
                  <td>{result.company.location}</td>
                  <td>
                    <span className={`source-badge source-${result.company.source?.toLowerCase() || "web"}`}>
                      {result.company.source === "Google Places" ? "Google" : result.company.source === "OpenStreetMap" ? "OSM" : result.company.source === "SerpAPI" ? "SerpAPI" : result.company.source === "Manual" ? "Manual" : "Web"}
                    </span>
                  </td>
                  <td>
                    <div className="score-bar">
                      <div
                        className="score-fill"
                        style={{
                          width: `${result.match_score}%`,
                          backgroundColor: getScoreColor(result.match_score),
                        }}
                      />
                      <span>{result.match_score}%</span>
                    </div>
                  </td>
                  <td>{result.probability}%</td>
                  <td>
                    <span className={`badge ${getOpportunityBadge(result.opportunity_level)}`}>
                      {result.opportunity_level}
                    </span>
                  </td>
                  <td className="expand-icon">
                    {expandedId === result.company.id ? "▼" : "▶"}
                  </td>
                </tr>
                {expandedId === result.company.id && (
                  <tr className="detail-row">
                    <td colSpan="9">
                      <div className="detail-content">
                        <div className="detail-grid">
                          <div>
                            <h4>Descripción</h4>
                            <p>{result.company.description}</p>
                          </div>
                          <div>
                            <h4>Pain Points</h4>
                            <ul>
                              {result.company.pain_points.length > 0 ? (
                                result.company.pain_points.map((pp, i) => (
                                  <li key={i}>{pp}</li>
                                ))
                              ) : (
                                <li className="no-data">Sin detectar</li>
                              )}
                            </ul>
                          </div>
                          <div>
                            <h4>Factores de Match</h4>
                            <ul>
                              {result.matching_factors.map((f, i) => (
                                <li key={i}>{f}</li>
                              ))}
                            </ul>
                          </div>
                          <div>
                            <h4>Decisores</h4>
                            <p>{result.company.decision_makers.join(", ")}</p>
                            <h4>Presupuesto</h4>
                            <p className={`budget-${result.company.budget_range}`}>
                              {result.company.budget_range.charAt(0).toUpperCase() +
                                result.company.budget_range.slice(1)}
                            </p>
                          </div>
                        </div>

                        {result.ai_analysis && (
                          <div className="ai-analysis">
                            <h4>Análisis IA</h4>
                            <p>{result.ai_analysis}</p>
                          </div>
                        )}

                        {result.specific_opportunities && result.specific_opportunities.length > 0 && (
                          <div className="opportunities-section">
                            <h4>Oportunidades Específicas ({result.specific_opportunities.length})</h4>
                            <div className="opportunities-grid">
                              {result.specific_opportunities.map((opp, i) => (
                                <div key={i} className="opportunity-card">
                                  <div className="opportunity-header">
                                    <h5>{opp.title}</h5>
                                    <div className="opportunity-badges">
                                      <span className={`impact-badge ${getImpactBadge(opp.impact)}`}>
                                        Impacto: {opp.impact}
                                      </span>
                                      <span className={`effort-badge ${getEffortBadge(opp.effort)}`}>
                                        Esfuerzo: {opp.effort}
                                      </span>
                                    </div>
                                  </div>
                                  <p className="opportunity-desc">{opp.description}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="recommendation">
                          <strong>Recomendación:</strong> {result.recommendation}
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
