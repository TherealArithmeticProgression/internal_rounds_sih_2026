import Dexie from 'dexie'

/*
  DEPRECATED FOR APP USE -- kept only so nothing that imports `db` from here
  breaks unexpectedly. This file and db/indexedDB.js were both independently
  managing a "predictions" store with two DIFFERENT, incompatible schemas
  (this one auto-increments `id`; indexedDB.js keys on `clientId` and has a
  proper sync-status index). Camera.jsx was writing here while Home.jsx read
  from indexedDB.js in places -- a real data-loss bug, not a style issue.

  All app pages now use db/indexedDB.js exclusively (savePrediction,
  getRecentPredictions, etc.) as the single source of truth for offline
  storage, matching the offline-sync architecture already designed for the
  backend (clientId-based dedupe on sync).

  If anything outside this frontend still depends on `db` from this exact
  file, keep it -- but do not wire any new UI through it.
*/

export const db = new Dexie('CropDiseaseDB')

db.version(1).stores({
  predictions: '++id, image, timestamp, syncStatus, diseaseLabel, confidence'
})

// syncStatus values: 'pending' (saved offline, not yet sent to backend)
//                     'synced'  (successfully sent to backend)
