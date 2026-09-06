const API_URL = import.meta.env.VITE_API_URL || '/api';
let accessToken = null;

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