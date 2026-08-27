import { useRef, useState } from 'react'
import { db } from '../db/database'

function Camera() {
  const videoRef = useRef(null)
  const [stream, setStream] = useState(null)
  const [capturedImage, setCapturedImage] = useState(null)
  const [saved, setSaved] = useState(false)

  async function startCamera() {
    try {
      const s = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' } // back camera on phone
      })
      setStream(s)
      setSaved(false)
      setCapturedImage(null)
      if (videoRef.current) {
        videoRef.current.srcObject = s
      }
    } catch (err) {
      alert('Camera access nahi mil paya: ' + err.message)
    }
  }

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
  }

  function capturePhoto() {
    const video = videoRef.current
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext('2d').drawImage(video, 0, 0)
    const dataUrl = canvas.toDataURL('image/jpeg', 0.8)
    setCapturedImage(dataUrl)
    stopCamera()
  }

  async function saveOffline() {
    await db.predictions.add({
      image: capturedImage,
      timestamp: new Date().toISOString(),
      syncStatus: 'pending',
      diseaseLabel: null,
      confidence: null
    })
    setSaved(true)
  }

  function retake() {
    setCapturedImage(null)
    setSaved(false)
    startCamera()
  }

  return (
    <div className="page">
      <h1>Scan Leaf</h1>
      <p className="page-subtitle">Patte ki clear photo kheenchein</p>

      <div className="camera-preview">
        {!capturedImage && <video ref={videoRef} autoPlay playsInline />}
        {capturedImage && <img src={capturedImage} alt="Captured leaf" />}
      </div>

      {!stream && !capturedImage && (
        <button className="btn btn-primary" onClick={startCamera}>
          📷 Camera Kholo
        </button>
      )}

      {stream && !capturedImage && (
        <button className="btn btn-primary" onClick={capturePhoto}>
          Photo Kheecho
        </button>
      )}

      {capturedImage && !saved && (
        <div style={{ display: 'flex', gap: '0.6rem' }}>
          <button className="btn btn-secondary" style={{ flex: 1 }} onClick={retake}>
            Dobara Lo
          </button>
          <button className="btn btn-primary" style={{ flex: 1 }} onClick={saveOffline}>
            Save Karo
          </button>
        </div>
      )}

      {saved && (
        <div className="card">
          <span className="status-pill status-pending">⏳ Pending Sync</span>
          <p style={{ marginTop: '0.6rem' }}>
            Photo save ho gayi. Internet aane pe automatically backend ko bhej di jayegi.
          </p>
          <button className="btn btn-secondary" style={{ marginTop: '0.8rem', width: '100%' }} onClick={retake}>
            Naya Scan Lo
          </button>
        </div>
      )}
    </div>
  )
}

export default Camera