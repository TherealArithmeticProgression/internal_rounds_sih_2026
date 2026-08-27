import { useEffect, useState } from 'react'
import { db } from '../db/database'
import { Link } from 'react-router-dom'

function Home() {
  const [scans, setScans] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadScans() {
      // Sabse recent 5 scans nikaalo, naye se purane order mein
      const all = await db.predictions.orderBy('timestamp').reverse().limit(5).toArray()
      setScans(all)
      setLoading(false)
    }
    loadScans()
  }, [])

  const pendingCount = scans.filter(s => s.syncStatus === 'pending').length

  function formatTime(isoString) {
    const date = new Date(isoString)
    return date.toLocaleString('en-IN', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="page">
      <h1>Dashboard</h1>
      <p className="page-subtitle">Aapke farm ka live overview</p>

      <div className="card">
        <div className="card-label">Current Risk</div>
        <p>Koi active alert nahi hai abhi</p>
      </div>

      {pendingCount > 0 && (
        <div className="card">
          <div className="card-label">Sync Status</div>
          <span className="status-pill status-pending">
            ⏳ {pendingCount} scan{pendingCount > 1 ? 's' : ''} pending sync
          </span>
        </div>
      )}

      <div className="card">
        <div className="card-label">Recent Scans</div>

        {loading && <p style={{ color: 'var(--text-muted)' }}>Loading...</p>}

        {!loading && scans.length === 0 && (
          <p style={{ color: 'var(--text-muted)' }}>Koi scan nahi hua abhi tak</p>
        )}

        {!loading && scans.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.7rem', marginTop: '0.5rem' }}>
            {scans.map(scan => (
              <div
                key={scan.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.7rem',
                  paddingBottom: '0.7rem',
                  borderBottom: '1px solid var(--border)'
                }}
              >
                <img
                  src={scan.image}
                  alt="scan"
                  style={{ width: '48px', height: '48px', borderRadius: '10px', objectFit: 'cover' }}
                />
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.85rem' }}>
                    {scan.diseaseLabel || 'Analysis pending'}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {formatTime(scan.timestamp)}
                  </div>
                </div>
                <span className={`status-pill ${scan.syncStatus === 'synced' ? 'status-synced' : 'status-pending'}`}>
                  {scan.syncStatus === 'synced' ? '✓ Synced' : '⏳ Pending'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {scans.length === 0 && !loading && (
        <Link to="/camera" className="btn btn-primary" style={{ textDecoration: 'none', display: 'block', textAlign: 'center' }}>
          📷 Pehla Scan Lo
        </Link>
      )}
    </div>
  )
}

export default Home