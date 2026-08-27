import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Home from './pages/Home'
import Camera from './pages/Camera'
import RiskScore from './pages/RiskScore'
import Result from './pages/Result'
import Settings from './pages/Settings'

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <div className="topbar">
          <div className="topbar-title">🌾 CropGuard</div>
        </div>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/camera" element={<Camera />} />
          <Route path="/risk-score" element={<RiskScore />} />
          <Route path="/result" element={<Result />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>

        <nav className="bottom-nav">
          <NavLink to="/" end className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="nav-icon">🏠</span>Home
          </NavLink>
          <NavLink to="/camera" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="nav-icon">📷</span>Scan
          </NavLink>
          <NavLink to="/risk-score" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="nav-icon">⚠️</span>Risk
          </NavLink>
          <NavLink to="/result" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="nav-icon">📋</span>Result
          </NavLink>
          <NavLink to="/settings" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="nav-icon">⚙️</span>Settings
          </NavLink>
        </nav>
      </div>
    </BrowserRouter>
  )
}

export default App