import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { useEffect } from 'react'
import { addSensorData } from './db/indexedDB'
import Home from './pages/Home'
import Camera from './pages/Camera'
import RiskScore from './pages/RiskScore'
import Result from './pages/Result'
import Settings from './pages/Settings'
import Login from './pages/Login'
import { useTranslation } from 'react-i18next'

function App() {
  const { t } = useTranslation();

  useEffect(() => {
    // Global function for sensor integration
    window.receiveSensorData = async (data) => {
      const allowed = ['temperature', 'humidity', 'soil_moisture', 'rainfall_mm'];
      const reading = Object.fromEntries(allowed.filter((key) => Number.isFinite(Number(data?.[key]))).map((key) => [key, Number(data[key])]));
      if (!Object.keys(reading).length) throw new TypeError('Sensor payload needs numeric telemetry values.');
      if (reading.humidity != null && (reading.humidity < 0 || reading.humidity > 100)) throw new RangeError('Humidity must be a percentage between 0 and 100.');
      if (reading.soil_moisture != null && (reading.soil_moisture < 0 || reading.soil_moisture > 100)) throw new RangeError('Soil moisture must be a percentage between 0 and 100.');
      if (reading.rainfall_mm != null && reading.rainfall_mm < 0) throw new RangeError('Rainfall cannot be negative.');
      if (data?.recorded_at) reading.recorded_at = new Date(data.recorded_at).toISOString();
      await addSensorData(reading);
      // Could dispatch a custom event here so React components can react instantly
      window.dispatchEvent(new CustomEvent('sensorDataUpdated', { detail: reading }));
    };
    return () => { delete window.receiveSensorData; };
  }, []);

  return (
    <BrowserRouter>
      <div className="app-shell" style={{ backgroundColor: '#f0f5f1', minHeight: '100vh', color: '#1f4620' }}>
        <div className="topbar" style={{ backgroundColor: '#1f4620', color: 'white', padding: '15px', textAlign: 'center', fontSize: '24px', fontWeight: 'bold' }}>
          <div className="topbar-title">🌿 CropGuard</div>
        </div>

        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Home />} />
          <Route path="/camera" element={<Camera />} />
          <Route path="/risk-score" element={<RiskScore />} />
          <Route path="/result" element={<Result />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>

        <nav className="bottom-nav" style={{ backgroundColor: '#ffffff', borderTop: '2px solid #1f4620' }}>
          <NavLink to="/" end className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="nav-icon">🏠</span>{t('home')}
          </NavLink>
          <NavLink to="/camera" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="nav-icon">📷</span>{t('scan')}
          </NavLink>
          <NavLink to="/risk-score" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="nav-icon">⚠️</span>{t('risk')}
          </NavLink>
          <NavLink to="/result" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="nav-icon">📋</span>{t('result')}
          </NavLink>
          <NavLink to="/settings" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="nav-icon">⚙️</span>{t('settings')}
          </NavLink>
        </nav>
      </div>
    </BrowserRouter>
  )
}

export default App
