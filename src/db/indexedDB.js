import { openDB } from 'idb';

const DB_NAME = 'cropguard-db';
const DB_VERSION = 2;

export async function initDB() {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      if (!db.objectStoreNames.contains('preferences')) {
        db.createObjectStore('preferences');
      }
      if (!db.objectStoreNames.contains('sensorData')) {
        db.createObjectStore('sensorData', { keyPath: 'id', autoIncrement: true });
      }
      if (!db.objectStoreNames.contains('outbreaks')) {
        db.createObjectStore('outbreaks', { keyPath: 'id', autoIncrement: true });
      }
      if (!db.objectStoreNames.contains('predictions')) {
        const predictions = db.createObjectStore('predictions', { keyPath: 'clientId' });
        predictions.createIndex('by-created-at', 'createdAt');
        predictions.createIndex('by-sync-status', 'syncStatus');
      }
    },
  });
}

export async function setPreference(key, value) {
  const db = await initDB();
  return db.put('preferences', value, key);
}

export async function getPreference(key) {
  const db = await initDB();
  return db.get('preferences', key);
}

export async function addSensorData(data) {
  const db = await initDB();
  return db.add('sensorData', { ...data, timestamp: new Date().toISOString() });
}

export async function savePrediction(prediction) {
  const db = await initDB();
  return db.put('predictions', prediction);
}

export async function getRecentPredictions(limit = 5) {
  const db = await initDB();
  const all = await db.getAll('predictions');
  return all.sort((a, b) => b.createdAt.localeCompare(a.createdAt)).slice(0, limit);
}

export async function getLatestSensorData() {
  const db = await initDB();
  const all = await db.getAll('sensorData');
  return all.length > 0 ? all[all.length - 1] : null;
}
