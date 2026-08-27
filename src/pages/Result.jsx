import { mockRiskScore } from '../mock/mockData'
import { mockPrediction } from '../mock/mockData'
// phir prediction = mockPrediction
// phir riskLevel, riskScore, sensors sab mockRiskScore.xxx se lo
function Result() {
  // Abhi dummy data hai - baad mein backend se real prediction aayega
  const hasResult = true
  const prediction = {
    disease: 'Bacterial Leaf Blight',
    confidence: 87,
    treatment: 'Copper-based bactericide spray karein. Affected leaves hata dein aur field mein paani ka bahav sudharein.'
  }

  if (!hasResult) {
    return (
      <div className="page">
        <h1>Result</h1>
        <p className="page-subtitle">Koi result available nahi hai</p>
        <div className="card">
          <p>Pehle Scan tab se ek photo lein.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="page">
      <h1>Scan Result</h1>
      <p className="page-subtitle">Latest scan ka analysis</p>

      <div className="card">
        <div className="card-label">Detected Disease</div>
        <h2 style={{ color: 'var(--accent)', margin: '0.3rem 0' }}>{prediction.disease}</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.5rem' }}>
          <div style={{
            flex: 1,
            height: '8px',
            background: 'var(--surface-light)',
            borderRadius: '999px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${prediction.confidence}%`,
              height: '100%',
              background: 'var(--accent)',
              borderRadius: '999px'
            }} />
          </div>
          <strong style={{ fontSize: '0.9rem' }}>{prediction.confidence}%</strong>
        </div>
      </div>

      <div className="card">
        <div className="card-label">Recommended Treatment</div>
        <p style={{ marginTop: '0.4rem' }}>{prediction.treatment}</p>
      </div>

      <div style={{ display: 'flex', gap: '0.6rem', marginTop: '1rem' }}>
        <button className="btn btn-secondary" style={{ flex: 1 }}>👍 Sahi Tha</button>
        <button className="btn btn-secondary" style={{ flex: 1 }}>👎 Galat Tha</button>
      </div>
    </div>
  )
}

export default Result