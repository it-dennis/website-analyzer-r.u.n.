import { useState } from 'react';
import { Globe, Search, ShieldCheck, FileBarChart2, BookText, AlertCircle } from 'lucide-react';
import { analyzeUrl } from './api';
import { AnalysisResult } from './types';
import UrlInput from './components/UrlInput';
import ScoreRing from './components/ScoreRing';
import SectionCard from './components/SectionCard';
import CheckList from './components/CheckList';
import PerformanceSection from './components/PerformanceSection';
import ContentSection from './components/ContentSection';
import ExportBar from './components/ExportBar';

const BOOKING_URL = import.meta.env.VITE_BOOKING_URL || '#';

const initialUrl = new URLSearchParams(window.location.search).get('url') ?? '';

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  async function handleAnalyze(url: string) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeUrl(url);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unbekannter Fehler');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center gap-3">
          <div className="flex items-center gap-2 text-blue-600">
            <Globe size={22} />
            <span className="font-bold text-lg text-gray-900">R.U.N.</span>
          </div>
          <span className="text-xs text-gray-400 hidden sm:block">Rapid URL Navigator</span>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8 space-y-8">
        {/* Search */}
        <div className="text-center space-y-4">
          {!result && !loading && (
            <>
              <h1 className="text-3xl font-bold text-gray-900">Website analysieren</h1>
              <p className="text-gray-500 text-sm max-w-lg mx-auto">
                SEO, Performance, Sicherheit und Content-Analyse — kostenlos und sofort.
              </p>
            </>
          )}
          <UrlInput onSubmit={handleAnalyze} loading={loading} initialValue={initialUrl} />
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-16 space-y-3">
            <div className="inline-flex items-center gap-3 text-blue-600">
              <svg className="animate-spin h-6 w-6" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <span className="text-lg font-medium">Analysiere Website…</span>
            </div>
            <p className="text-sm text-gray-400">Das kann bis zu 30 Sekunden dauern (inkl. PageSpeed API)</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="flex items-start gap-3 bg-red-50 border border-red-200 rounded-xl p-4">
            <AlertCircle size={18} className="text-red-600 mt-0.5 shrink-0" />
            <div>
              <p className="text-sm font-medium text-red-700">Analyse fehlgeschlagen</p>
              <p className="text-sm text-red-600 mt-0.5">{error}</p>
            </div>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* Overview Bar */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Analysierte URL</p>
                  <a href={result.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 font-medium hover:underline break-all">
                    {result.url}
                  </a>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {new Date(result.analyzed_at).toLocaleString('de-DE')}
                    {result.response_time_ms && ` · ${result.response_time_ms}ms`}
                  </p>
                </div>
                <div className="flex items-center gap-8">
                  <div className="text-center">
                    <ScoreRing score={result.overall_score} size={88} />
                    <p className="text-xs text-gray-500 mt-1 font-medium">Gesamt</p>
                  </div>
                  <div className="hidden sm:flex flex-col gap-2 text-sm text-gray-600">
                    {[
                      { label: 'SEO', score: result.seo.score },
                      { label: 'Performance', score: result.performance.score ?? null },
                      { label: 'Sicherheit', score: result.security.score },
                      { label: 'Content', score: result.content.score },
                    ].map(({ label, score }) => (
                      <div key={label} className="flex items-center gap-2">
                        <span className="w-20 text-right text-xs text-gray-500">{label}</span>
                        <div className="w-32 h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all"
                            style={{
                              width: `${score ?? 0}%`,
                              backgroundColor: score === null ? '#9ca3af' : score >= 80 ? '#22c55e' : score >= 50 ? '#eab308' : '#ef4444',
                            }}
                          />
                        </div>
                        <span className="text-xs font-medium w-8">{score ?? '–'}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {result.http_status !== undefined && result.http_status >= 400 && (
              <div className="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-xl p-4">
                <AlertCircle size={18} className="text-amber-600 mt-0.5 shrink-0" />
                <p className="text-sm text-amber-800">
                  Die Seite hat mit <strong>HTTP {result.http_status}</strong> geantwortet. Die Ergebnisse beziehen sich auf diese Fehlerseite und sind nur eingeschränkt aussagekräftig.
                </p>
              </div>
            )}

            <ExportBar data={result} />

            {/* Booking CTA */}
            {BOOKING_URL !== '#' && (
              <div className="flex items-center justify-between gap-4 bg-blue-50 border border-blue-200 rounded-xl p-5">
                <div>
                  <p className="font-semibold text-blue-900 text-sm">Tiefer einsteigen?</p>
                  <p className="text-xs text-blue-700 mt-0.5">
                    Professioneller Audit mit PDF-Report, manueller Sichtprüfung und konkretem Angebot — in 48&nbsp;h.
                  </p>
                </div>
                <a
                  href={`${BOOKING_URL}?url=${encodeURIComponent(result.url)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="shrink-0 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors whitespace-nowrap"
                >
                  Audit buchen →
                </a>
              </div>
            )}

            {/* Section Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              <SectionCard title="SEO" icon={<Search size={16} />} score={result.seo.score} error={result.seo.error}>
                <CheckList checks={result.seo.checks} />
              </SectionCard>

              <SectionCard title="Performance" icon={<FileBarChart2 size={16} />} score={result.performance.score ?? null} error={undefined}>
                <PerformanceSection data={result.performance} />
              </SectionCard>

              <SectionCard title="Sicherheit" icon={<ShieldCheck size={16} />} score={result.security.score} error={result.security.error}>
                <CheckList checks={result.security.checks} />
              </SectionCard>

              <SectionCard title="Content" icon={<BookText size={16} />} score={result.content.score} error={result.content.error}>
                <ContentSection data={result.content} />
              </SectionCard>
            </div>

            {/* Recommendations Summary */}
            {(() => {
              const allRecs = [
                ...result.seo.checks,
                ...result.security.checks,
                ...result.content.checks,
              ].filter(c => (c.status === 'fail' || c.status === 'warning') && c.recommendation);
              if (!allRecs.length) return null;
              return (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-5">
                  <h3 className="font-semibold text-amber-800 mb-3">Wichtigste Handlungsempfehlungen</h3>
                  <ol className="space-y-2">
                    {allRecs.map((r, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-amber-900">
                        <span className="font-bold shrink-0">{i + 1}.</span>
                        <span><strong>{r.name}:</strong> {r.recommendation}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              );
            })()}
          </div>
        )}
      </main>

      <footer className="text-center text-xs text-gray-400 py-8 border-t border-gray-100 mt-8">
        R.U.N. – Rapid URL Navigator · Made with ❤️ for better websites
      </footer>
    </div>
  );
}
