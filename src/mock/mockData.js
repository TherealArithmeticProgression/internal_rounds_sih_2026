// Kept as a dev-time fallback only. No page imports this anymore -- Result.jsx
// and RiskScore.jsx now read real data from IndexedDB / the API. Useful if
// you want to stub the UI before the backend endpoints are live.

export const mockRiskScore = {
  score: 22,
  level: 'low',
  message: 'Conditions currently look safe',
};

export const mockPrediction = {
  disease: 'Bacterial Leaf Spot',
  confidence: 87,
  treatment: 'Apply a copper-based bactericide. Remove affected leaves and improve field drainage.',
};
