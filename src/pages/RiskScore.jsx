import React, { useState } from 'react';
// import { mockRiskScore } from '../mock/mockData'
// import { mockPrediction } from '../mock/mockData'

const SERVICE_UUID = '4fafc201-1fb5-459e-8fcc-c5c9c331914b';
const CHARACTERISTIC_UUID = 'beb5483e-36e1-4688-b7f5-ea07361b26a8';

function RiskScore() {
  // State variables for our live sensor data
  const [temperature, setTemperature] = useState('--');
  const [humidity, setHumidity] = useState('--');
  const [moisture, setMoisture] = useState('--');
  const [statusText, setStatusText] = useState('Waiting for data...');

  // Mock data for Risk Score (can be replaced by backend logic later)
  const riskLevel = 'low'; // 'low' | 'medium' | 'high'
  const riskScore = 22;

  const levelConfig = {
    low: { color: '#8bc34a', label: 'Low Risk', message: 'Abhi conditions safe hain' },
    medium: { color: '#e0a72e', label: 'Medium Risk', message: 'Nazar rakho, conditions badal rahi hain' },
    high: { color: '#d9534f', label: 'High Risk', message: 'Turant dhyan dein — outbreak ka khatra hai' }
  };

  const current = levelConfig[riskLevel];

  // The Web Bluetooth connection function
  const connectToNode = async () => {
    try {
      setStatusText('Requesting Bluetooth Device...');
      const device = await navigator.bluetooth.requestDevice({
        filters: [{ name: 'AgriNode' }],
        optionalServices: [SERVICE_UUID]
      });

      setStatusText('Connecting to Node...');
      const server = await device.gatt.connect();

      setStatusText('Getting Service...');
      const service = await server.getPrimaryService(SERVICE_UUID);

      setStatusText('Getting Characteristic...');
      const characteristic = await service.getCharacteristic(CHARACTERISTIC_UUID);

      setStatusText('Reading Sensor Data...');
      const value = await characteristic.readValue();
      
      // Decode the raw bytes into a string
      const decoder = new TextDecoder('utf-8');
      const sensorString = decoder.decode(value);
      
      // Split "Temp,Humidity,Moisture" into individual variables
      const dataArray = sensorString.split(',');
      
      // Update the React state to automatically re-render the UI
      setTemperature(dataArray[0]);
      setHumidity(dataArray[1]);
      setMoisture(dataArray[2]);
      
      setStatusText('Connected and synced!');

    } catch (error) {
      console.error('Connection failed!', error);
      setStatusText('Connection failed. Check console.');
    }
  };

  return (
    <div className="page">
      <h1>Risk Score</h1>
      <p className="page-subtitle">Environment data ke basis par outbreak risk</p>

      {/* Risk Score Dial Card */}
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

      {/* BLE Connection Area */}
      <div style={{ textAlign: 'center', margin: '1rem 0' }}>
        <button 
          onClick={connectToNode} 
          style={{ padding: '0.5rem 1rem', cursor: 'pointer', borderRadius: '5px' }}
        >
          Connect to Sensor Node
        </button>
        <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          {statusText}
        </div>
      </div>

      {/* Live Sensor Readings Card */}
      <div className="card">
        <div className="card-label">Sensor Readings</div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem' }}>
          <span>🌡️ Temperature</span>
          <strong>{temperature !== '--' ? `${temperature}°C` : '--'}</strong>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem' }}>
          <span>💧 Humidity</span>
          <strong>{humidity !== '--' ? `${humidity}%` : '--'}</strong>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem' }}>
          <span>🌱 Soil Moisture</span>
          <strong>{moisture}</strong>
        </div>
      </div>

      <div className="card">
        <div className="card-label">Why this score</div>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          Rice Blast ke liye risk tab badhta hai jab humidity 90% se upar ho aur temperature 17-28°C ke beech ho, saath mein 7+ ghante leaf wetness ho.
        </p>
      </div>
    </div>
  );
}

export default RiskScore;