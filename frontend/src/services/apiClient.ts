export const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://127.0.0.1:49281';

export async function fetchApi<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);
  if (!response.ok) {
    throw new Error(`API error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}
