// Ye file temporary hai - jab backend ready ho, in exports ko
// real API calls se replace kar denge (fetch/axios)

export const mockRiskScore = {
  score: 22,
  level: 'low', // 'low' | 'medium' | 'high'
  message: 'Abhi conditions safe hain',
  sensors: {
    temperature: 26,
    humidity: 68,
    soilMoisture: 'Moderate'
  }
}

export const mockPrediction = {
  disease: 'Bacterial Leaf Blight',
  confidence: 87,
  treatment: 'Copper-based bactericide spray karein. Affected leaves hata dein aur field mein paani ka bahav sudharein.'
}