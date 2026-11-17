import { useState, MouseEvent, ReactNode } from 'react';
import { Search, ShieldCheck, FileBarChart2, BookText, AlertCircle, Gauge, ArrowLeft } from 'lucide-react';
import { analyzeUrl } from './api';
import { AnalysisResult } from './types';
import { usePage } from './route';
import UrlInput from './components/UrlInput';
import ScoreRing from './components/ScoreRing';
import SectionCard from './components/SectionCard';
import CheckList from './components/CheckList';
import PerformanceSection from './components/PerformanceSection';
import ContentSection from './components/ContentSection';
import ExportBar from './components/ExportBar';
import PromoCard from './components/PromoCard';
import Impressum from './components/legal/Impressum';
import Datenschutz from './components/legal/Datenschutz';

const initialUrl = new URLSearchParams(window.location.search).get('url') ?? '';

function barColor(score: number | null) {
  if (score === null) return '#75798c';
  return score >= 80 ? '#7ccf9a' : score >= 50 ? '#e6bd6f' : '#ee8a8a';
}

function Header({ onHome }: { onHome: (e: MouseEvent) => void }) {
  return (
    <header className="sticky top-0 z-10 border-b border-line bg-bg/85 backdrop-blur">
      <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between gap-4">
        <a href="/" onClick={onHome} className="flex items-center gap-3 rounded-lg" aria-label="R.U.N. – Rapid URL Navigator, zur Startseite">
          {/* Markenbuch: 48–120 px Breite = flache Variante */}
          <img src="/run-logo-flach-dunkel.svg" width={86} height={40} alt="" />
          <span className="hidden sm:block leading-tight">
            <span className="block text-sm text-ink">Rapid URL Navigator</span>
            <span className="block text-xs text-neutral-500">Website Analyzer</span>
          </span>
        </a>
        <a href="mailto:info@dennisrapp.com" className="text-xs text-neutral-400 hover:text-accent-300 transition-colors">
          Ein Angebot der Dennis Rapp IT-Agency
        </a>
      </div>
    </header>
  );
}

function Footer({ go }: { go: (to: string) => (e: MouseEvent) => void }) {
  const link = 'text-neutral-400 hover:text-accent-300 transition-colors';
  return (
    <footer className="border-t border-line mt-12">
      <div className="max-w-5xl mx-auto px-4 py-8 flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between text-xs text-neutral-500">
        <p>R.U.N. – Rapid URL Navigator · ein Angebot der Dennis Rapp IT-Agency</p>
        <nav className="flex gap-5" aria-label="Rechtliches">
          <a href="/impressum" onClick={go('/impressum')} className={link}>Impressum</a>
          <a href="/datenschutz" onClick={go('/datenschutz')} className={link}>Datenschutz</a>
          <a href="mailto:info@dennisrapp.com" className={link}>Kontakt</a>
        </nav>
      </div>
    </footer>
  );
}

function Shell({ children, navigate }: { children: ReactNode; navigate: (to: string) => void }) {
  const go = (to: string) => (e: MouseEvent) => {
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
    e.preventDefault();
    navigate(to);
  };
  return (
    <div className="min-h-screen flex flex-col">
      <Header onHome={go('/')} />
      <main className="flex-1 w-full max-w-5xl mx-auto px-4 py-10">{children}</main>
      <Footer go={go} />
    </div>
  );
}

export default function App() {
  const [page, navigate] = usePage();
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

  if (page === 'impressum' || page === 'datenschutz') {
    return (
      <Shell navigate={navigate}>
        <a
          href="/"
          onClick={e => { e.preventDefault(); navigate('/'); }}
          className="inline-flex items-center gap-1.5 text-sm text-neutral-400 hover:text-accent-300 transition-colors mb-6"
        >
          <ArrowLeft size={15} /> Zurück zur Analyse
        </a>
        {page === 'impressum' ? <Impressum /> : <Datenschutz />}
      </Shell>
    );
  }

  const hero = !result && !loading;

  return (
    <Shell navigate={navigate}>
      <div className="space-y-10">
        {/* Start / Eingabe */}
        {hero ? (
          <section className="grid gap-10 lg:grid-cols-[1.15fr_1fr] lg:items-center">
            <div className="space-y-6">
              <p className="inline-flex items-center gap-2 rounded-full border border-accent/30 bg-accent/10 px-3 py-1 text-xs text-accent-300">
                <Gauge size={13} /> Kostenlos, ohne Anmeldung
              </p>
              <h1 className="text-4xl sm:text-5xl leading-[1.1] text-ink">Ihre Website, in Sekunden analysiert</h1>
              <p className="text-neutral-400 max-w-lg leading-relaxed">
                R.U.N. prüft Ladezeit, Suchmaschinen-Tauglichkeit, Sicherheit und Inhalt Ihrer Seite und zeigt, wo sie Tempo verliert.
              </p>
              <UrlInput onSubmit={handleAnalyze} loading={loading} initialValue={initialUrl} />
              <ul className="flex flex-wrap gap-x-5 gap-y-2 text-xs text-neutral-500">
                {[[Search, 'SEO'], [FileBarChart2, 'Performance'], [ShieldCheck, 'Sicherheit'], [BookText, 'Content']].map(([Icon, label]) => {
                  const I = Icon as typeof Search;
                  return <li key={label as string} className="flex items-center gap-1.5"><I size={14} className="text-accent" /> {label as string}</li>;
                })}
              </ul>
            </div>
            <div className="flex justify-center lg:justify-end">
              <img
                src="/run-logo-collage-dunkel.svg"
                width={420}
                height={194}
                alt="R.U.N. – drei Buchstaben aus Läuferbeinen"
                className="w-full max-w-[340px] lg:max-w-[420px] h-auto"
              />
            </div>
          </section>
        ) : (
          <section className="max-w-2xl">
            <UrlInput onSubmit={handleAnalyze} loading={loading} initialValue={result ? '' : initialUrl} />
          </section>
        )}

        {hero && <PromoCard />}

        {/* Loading State */}
        {loading && (
          <div className="card py-14 text-center space-y-3" role="status">
            <div className="inline-flex items-center gap-3 text-accent-300">
              <svg className="animate-spin h-6 w-6" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <span className="text-lg">Analysiere Website …</span>
            </div>
            <p className="text-sm text-neutral-500">Das kann bis zu einer Minute dauern.</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="flex items-start gap-3 bg-bad/10 border border-bad/30 rounded-lg p-4" role="alert">
            <AlertCircle size={18} className="text-bad mt-0.5 shrink-0" />
            <div>
              <p className="text-sm text-bad">Analyse fehlgeschlagen</p>
              <p className="text-sm text-neutral-300 mt-0.5">{error}</p>
            </div>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* Overview Bar */}
            <div className="card p-6">
              <div className="flex flex-wrap items-center justify-between gap-6">
                <div className="min-w-0">
                  <p className="text-xs text-neutral-500 uppercase tracking-wider">Analysierte URL</p>
                  <a href={result.url} target="_blank" rel="noopener noreferrer" className="text-accent-300 text-lg hover:underline break-all">
                    {result.url}
                  </a>
                  <p className="text-xs text-neutral-500 mt-1">
                    {new Date(result.analyzed_at).toLocaleString('de-DE')}
                    {result.response_time_ms && ` · ${(result.response_time_ms / 1000).toFixed(1).replace('.', ',')} s`}
                  </p>
                </div>
                <div className="flex items-center gap-8">
                  <div className="text-center">
                    <ScoreRing score={result.overall_score} size={96} />
                    <p className="text-xs text-neutral-400 mt-1">Gesamt</p>
                  </div>
                  <div className="hidden sm:flex flex-col gap-2 text-sm">
                    {[
                      { label: 'SEO', score: result.seo.score },
                      { label: 'Performance', score: result.performance.score ?? null },
                      { label: 'Sicherheit', score: result.security.score },
                      { label: 'Content', score: result.content.score },
                    ].map(({ label, score }) => (
                      <div key={label} className="flex items-center gap-2">
                        <span className="w-24 text-right text-xs text-neutral-400">{label}</span>
                        <div className="w-32 h-1.5 bg-white/10 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all"
                            style={{ width: `${score ?? 0}%`, backgroundColor: barColor(score) }}
                          />
                        </div>
                        <span className="text-xs text-neutral-300 w-8">{score ?? '–'}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {result.http_status !== undefined && result.http_status >= 400 && (
              <div className="flex items-start gap-3 bg-warn/10 border border-warn/30 rounded-lg p-4" role="alert">
                <AlertCircle size={18} className="text-warn mt-0.5 shrink-0" />
                <p className="text-sm text-neutral-200">
                  Die Seite hat mit <strong className="font-medium text-warn">HTTP {result.http_status}</strong> geantwortet. Die Ergebnisse beziehen sich auf diese Fehlerseite und sind nur eingeschränkt aussagekräftig.
                  {[401, 403, 406, 429].includes(result.http_status) && (
                    <> Das deutet darauf hin, dass die Seite automatische Prüfungen blockiert (z. B. durch Bot-Schutz oder Firewall). Erlauben Sie dem User-Agent <code className="rounded bg-white/10 px-1">WebCheckAnalyzer</code> den Zugriff oder prüfen Sie die Seite ohne Schutz.</>
                  )}
                </p>
              </div>
            )}

            <ExportBar data={result} />

            {/* Section Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              <SectionCard title="SEO" icon={<Search size={17} />} score={result.seo.score} error={result.seo.error}>
                <CheckList checks={result.seo.checks} />
              </SectionCard>

              <SectionCard title="Performance" icon={<FileBarChart2 size={17} />} score={result.performance.score ?? null} error={undefined}>
                <PerformanceSection data={result.performance} />
              </SectionCard>

              <SectionCard title="Sicherheit" icon={<ShieldCheck size={17} />} score={result.security.score} error={result.security.error}>
                <CheckList checks={result.security.checks} />
              </SectionCard>

              <SectionCard title="Content" icon={<BookText size={17} />} score={result.content.score} error={result.content.error}>
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
                <section className="card p-6">
                  <h3 className="text-base text-ink mb-4">Wichtigste Handlungsempfehlungen</h3>
                  <ol className="space-y-2.5">
                    {allRecs.map((r, i) => (
                      <li key={i} className="flex items-start gap-3 text-sm text-neutral-300">
                        <span className="shrink-0 w-6 h-6 rounded-full bg-accent/15 text-accent-300 text-xs flex items-center justify-center">{i + 1}</span>
                        <span><span className="text-ink">{r.name}:</span> {r.recommendation}</span>
                      </li>
                    ))}
                  </ol>
                </section>
              );
            })()}

            <PromoCard scannedUrl={result.url} />
          </div>
        )}
      </div>
    </Shell>
  );
}
