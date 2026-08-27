import { mockRiskScore } from '../mock/mockData'
// phir riskLevel, riskScore, sensors sab mockRiskScore.xxx se lo
import { mockPrediction } from '../mock/mockData'
// phir prediction = mockPrediction
function RiskScore() {
  // Abhi dummy data hai - baad mein backend se real risk score aayega
  const riskLevel = 'low' // 'low' | 'medium' | 'high'
  const riskScore = 22

  const levelConfig = {
    low: { color: '#8bc34a', label: 'Low Risk', message: 'Abhi conditions safe hain' },
    medium: { color: '#e0a72e', label: 'Medium Risk', message: 'Nazar rakho, conditions badal rahi hain' },
    high: { color: '#d9534f', label: 'High Risk', message: 'Turant dhyan dein — outbreak ka khatra hai' }
  }

  const current = levelConfig[riskLevel]

  return (
    <div className="page">
      <h1>Risk Score</h1>
      <p className="page-subtitle">Environment data ke basis par outbreak risk</p>

      <div className="card" style={{ textAlign: 'center', padding: '2rem 1rem' }}>
        <div style={{
          width: '140px',
          height: '140px',
          borderRadius: '50%',
          border: `10px solid ${current.color}`,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 1rem'
        }}>
          <div style={{ fontSize: '2.2rem', fontWeight: 700 }}>{riskScore}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>/ 100</div>
        </div>
        <div style={{ color: current.color, fontWeight: 700, fontSize: '1.1rem', marginBottom: '0.3rem' }}>
          {current.label}
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{current.message}</p>
      </div>

      <div className="card">
        <div className="card-label">Sensor Readings</div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem' }}>
          <span>🌡️ Temperature</span>
          <strong>26°C</strong>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem' }}>
          <span>💧 Humidity</span>
          <strong>68%</strong>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem' }}>
          <span>🌱 Soil Moisture</span>
          <strong>Moderate</strong>
        </div>
      </div>

      <div className="card">
        <div className="card-label">Why this score</div>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          Rice Blast ke liye risk tab badhta hai jab humidity 90% se upar ho aur temperature 17-28°C ke beech ho, saath mein 7+ ghante leaf wetness ho.
        </p>
      </div>
    </div>
  )
}

export default RiskScore