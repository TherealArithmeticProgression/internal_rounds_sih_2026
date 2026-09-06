import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { setPreference } from '../db/indexedDB';
import { requestOtp, verifyOtp } from '../services/api';

export default function Login() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  
  const [phoneNumber, setPhoneNumber] = useState('');
  const [otp, setOtp] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [activeField, setActiveField] = useState('phone'); // 'phone' or 'otp'
  const [lang, setLang] = useState('hi'); // Default Hindi
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);

  // Initialize Web Speech API
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = SpeechRecognition ? new SpeechRecognition() : null;

  useEffect(() => {
    i18n.changeLanguage(lang);
  }, [lang, i18n]);

  const handleListen = (field) => {
    if (!recognition) {
      alert("Voice recognition not supported in this browser.");
      return;
    }
    
    setActiveField(field);
    setIsListening(true);
    
    // Attempt to map our shortcodes to valid BCP47 for Speech API
    const langMap = {
      'hi': 'hi-IN',
      'pa': 'pa-IN',
      'bn': 'bn-IN',
      'ta': 'ta-IN',
      'en': 'en-IN'
    };
    
    // If Punjabi, we warn but still try to use pa-IN or fallback to hi-IN based on user setup
    recognition.lang = langMap[lang] || 'hi-IN';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      // Extract digits from the transcript (some languages might spell out numbers, but we try extracting raw digits)
      const digits = transcript.replace(/[^0-9]/g, '');
      
      if (digits) {
        if (field === 'phone') {
          setPhoneNumber(prev => prev + digits);
        } else {
          setOtp(prev => prev + digits);
        }
      }
      setIsListening(false);
    };

    recognition.onerror = (event) => {
      console.error(event.error);
      setIsListening(false);
    };
    
    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  const handleRequestOtp = async () => {
    setBusy(true);
    try {
      const result = await requestOtp(phoneNumber);
      setMessage(result.detail || 'Verification code sent.');
    } catch (error) {
      setMessage(error.message);
    } finally { setBusy(false); }
  };

  const handleLogin = async () => {
    setBusy(true);
    try {
      await verifyOtp(phoneNumber, otp, lang);
      await setPreference('userPhone', phoneNumber);
      await setPreference('userLang', lang);
      navigate('/');
    } catch (error) { setMessage(error.message); }
    finally { setBusy(false); }
  };

  return (
    <div className="login-container" style={{ padding: '20px', maxWidth: '400px', margin: '0 auto' }}>
      <h2>{t('login_title')}</h2>
      
      <div style={{ marginBottom: '15px' }}>
        <label>Language:</label>
        <select value={lang} onChange={(e) => setLang(e.target.value)} style={{ width: '100%', padding: '10px' }}>
          <option value="hi">हिंदी (Hindi)</option>
          <option value="pa">ਪੰਜਾਬੀ (Punjabi)</option>
          <option value="bn">বাংলা (Bengali)</option>
          <option value="ta">தமிழ் (Tamil)</option>
          <option value="en">English</option>
        </select>
      </div>

      {lang === 'pa' && (
        <div style={{ background: '#fff3cd', color: '#856404', padding: '10px', borderRadius: '5px', marginBottom: '15px' }}>
          {t('punjabi_warning')}
        </div>
      )}

      <div style={{ marginBottom: '15px' }}>
        <label>{t('phone_number')}:</label>
        <div style={{ display: 'flex' }}>
          <input 
            type="tel" inputMode="tel" autoComplete="tel" placeholder="+919876543210"
            value={phoneNumber} 
            onChange={e => setPhoneNumber(e.target.value)}
            style={{ flex: 1, padding: '10px' }}
          />
          <button 
            onClick={() => handleListen('phone')}
            style={{ background: isListening && activeField === 'phone' ? 'red' : '#4CAF50', color: 'white', padding: '10px' }}
          >
            🎤
          </button>
        </div>
      </div>

      <button disabled={busy} onClick={handleRequestOtp} style={{ width: '100%', padding: '10px', marginBottom: '15px' }}>
        {busy ? 'Please wait…' : 'Request OTP'}
      </button>

      <div style={{ marginBottom: '15px' }}>
        <label>{t('otp')}:</label>
        <div style={{ display: 'flex' }}>
          <input 
            type="text" inputMode="numeric" autoComplete="one-time-code" maxLength="6"
            value={otp} 
            onChange={e => setOtp(e.target.value)}
            style={{ flex: 1, padding: '10px' }}
          />
          <button 
            onClick={() => handleListen('otp')}
            style={{ background: isListening && activeField === 'otp' ? 'red' : '#4CAF50', color: 'white', padding: '10px' }}
          >
            🎤
          </button>
        </div>
      </div>

      {message && <p role="status" style={{ marginBottom: '15px' }}>{message}</p>}
      <button disabled={busy} onClick={handleLogin} style={{ width: '100%', padding: '15px', background: '#1f4620', color: 'white', fontSize: '18px' }}>
        {t('submit')}
      </button>
    </div>
  );
}
