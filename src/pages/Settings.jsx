import { useState } from 'react'

function Settings() {
  const [language, setLanguage] = useState('en')

  const languages = [
    { code: 'en', label: 'English' },
    { code: 'hi', label: 'हिंदी (Hindi)' },
    { code: 'pa', label: 'ਪੰਜਾਬੀ (Punjabi)' }
  ]

  return (
    <div className="page">
      <h1>Settings</h1>
      <p className="page-subtitle">App preferences aur account</p>

      <div className="card">
        <div className="card-label">Language</div>
        {languages.map(lang => (
          <div
            key={lang.code}
            onClick={() => setLanguage(lang.code)}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '0.7rem 0',
              borderBottom: '1px solid var(--border)',
              cursor: 'pointer'
            }}
          >
            <span>{lang.label}</span>
            {language === lang.code && <span style={{ color: 'var(--accent)' }}>✓</span>}
          </div>
        ))}
      </div>

      <div className="card">
        <div className="card-label">Farm Info</div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          Farm details yahan add honge (name, location, crop type)
        </p>
      </div>

      <div className="card">
        <div className="card-label">About</div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          CropGuard v1.0 · SIH1638 · AI-Driven Crop Disease Prediction
        </p>
      </div>
    </div>
  )
}

export default Settings