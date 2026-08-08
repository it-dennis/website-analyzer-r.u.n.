import { AnalysisResult } from './types';

export async function analyzeUrl(url: string): Promise<AnalysisResult> {
  const res = await fetch('/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Server-Fehler: ${res.status}`);
  }
  return res.json();
}
