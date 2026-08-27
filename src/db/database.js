import Dexie from 'dexie'

// Database create karo
export const db = new Dexie('CropDiseaseDB')

// Table structure define karo
db.version(1).stores({
  predictions: '++id, image, timestamp, syncStatus, diseaseLabel, confidence'
})

// syncStatus values: 'pending' (offline save hua, backend ko nahi bheja abhi)
//                     'synced'  (backend ko successfully bhej diya)