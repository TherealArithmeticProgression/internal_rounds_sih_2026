const API_URL = import.meta.env.VITE_API_URL || '/api';
let accessToken = null;

// The exact UUIDs from your ESP32 code and screenshot
const SERVICE_UUID = '4fafc201-1fb5-459e-8fcc-c5c9c331914b';
const CHARACTERISTIC_UUID = 'beb5483e-36e1-4688-b7f5-ea07361b26a8';

document.getElementById('connectBtn').addEventListener('click', async () => {
  try {
    // 1. Request Bluetooth Device matching our Service UUID
    console.log('Requesting Bluetooth Device...');
    const device = await navigator.bluetooth.requestDevice({
      filters: [{ name: 'AgriNode' }],
      optionalServices: [SERVICE_UUID]
    });

    // 2. Connect to the GATT Server
    console.log('Connecting to GATT Server...');
    const server = await device.gatt.connect();

    // 3. Get the Service
    console.log('Getting Service...');
    const service = await server.getPrimaryService(SERVICE_UUID);

    // 4. Get the Characteristic
    console.log('Getting Characteristic...');
    const characteristic = await service.getCharacteristic(CHARACTERISTIC_UUID);

    // 5. Read the Value
    console.log('Reading Sensor Data...');
    const value = await characteristic.readValue();
    
    // 6. Decode the raw bytes into a readable string
    const decoder = new TextDecoder('utf-8');
    const sensorString = decoder.decode(value);
    
    // 7. Split the string into individual variables
    // sensorString format is "Temp,Humidity,Moisture"
    const dataArray = sensorString.split(',');
    const temperature = dataArray[0];
    const humidity = dataArray[1];
    const moisture = dataArray[2];

    // Display the results on your webpage
    document.getElementById('sensorDataDisplay').innerHTML = `
      Temperature: ${temperature} °C <br>
      Humidity: ${humidity} % <br>
      Raw Moisture: ${moisture}
    `;

  } catch (error) {
    console.error('Connection failed!', error);
    document.getElementById('sensorDataDisplay').innerText = 'Connection failed. See console.';
  }
});

export async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`);
  if (options.body && !(options.body instanceof FormData)) headers.set('Content-Type', 'application/json');
  const result = await fetch(`${API_URL}${path}`, { ...options, headers, credentials: 'include' });
  const payload = await result.json().catch(() => ({}));
  if (!result.ok) throw new Error(payload.detail || 'The request could not be completed.');
  return payload;
}

export async function requestOtp(phone_number) {
  return api('/auth/request-otp/', { method: 'POST', body: JSON.stringify({ phone_number }) });
}

export async function verifyOtp(phone_number, otp, language) {
  const session = await api('/auth/verify-otp/', { method: 'POST', body: JSON.stringify({ phone_number, otp, language }) });
  accessToken = session.access;
  return session;
}
