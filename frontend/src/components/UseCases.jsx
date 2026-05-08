export default function UseCases({ useCases }) {
  if (!useCases || useCases.length === 0) return null;

  const getUrgencyIcon = (urgency) => {
    switch (urgency) {
      case "alta":
        return "🔴";
      case "media":
        return "🟡";
      case "baja":
        return "🟢";
      default:
        return "⚪";
    }
  };

  return (
    <div className="usecases-section">
      <h2>Casos de Uso Puntuales</h2>
      <p className="section-subtitle">
        Escenarios específicos donde puedes suplir las necesidades del cliente
      </p>

      <div className="usecases-grid">
        {useCases.map((uc, index) => (
          <div key={index} className="usecase-card">
            <div className="usecase-header">
              <h3>{uc.company_name}</h3>
              <span className={`urgency-badge urgency-${uc.urgency}`}>
                {getUrgencyIcon(uc.urgency)} Urgencia: {uc.urgency}
              </span>
            </div>

            <div className="usecase-body">
              <div className="usecase-field">
                <h4>Escenario</h4>
                <p>{uc.scenario}</p>
              </div>

              <div className="usecase-field">
                <h4>Cómo acercarse</h4>
                <p>{uc.how_to_approach}</p>
              </div>

              <div className="usecase-field">
                <h4>Propuesta de Valor</h4>
                <p className="value-prop">{uc.value_proposition}</p>
              </div>

              <div className="usecase-field">
                <h4>Resultado Esperado</h4>
                <p>{uc.expected_outcome}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
