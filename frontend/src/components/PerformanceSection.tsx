import { PerformanceResult } from '../types';
import ScoreRing from './ScoreRing';

const METRIC_COLORS = {
  good: 'bg-green-100 text-green-800',
  'needs-improvement': 'bg-yellow-100 text-yellow-800',
  poor: 'bg-red-100 text-red-800',
  info: 'bg-gray-100 text-gray-700',
};

export default function PerformanceSection({ data }: { data: PerformanceResult }) {
  const { scores, metrics, error } = data;

  if (error) {
    return (
      <div className="space-y-3">
        <div className="text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-3">
          {error}
        </div>
        <p className="text-xs text-gray-500">
          Tipp: Hol dir einen kostenlosen{' '}
          <a href="https://developers.google.com/speed/docs/insights/v5/get-started" target="_blank" rel="noopener noreferrer" className="underline">
            PageSpeed Insights API-Key
          </a>{' '}
          und trag ihn in <code className="bg-gray-100 px-1 rounded">.env</code> ein.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {scores && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {scores.performance !== undefined && <ScoreRing score={scores.performance ?? 0} size={72} label="Performance" />}
          {scores.accessibility !== undefined && <ScoreRing score={scores.accessibility ?? 0} size={72} label="Accessibility" />}
          {scores.best_practices !== undefined && <ScoreRing score={scores.best_practices ?? 0} size={72} label="Best Practices" />}
          {scores.seo !== undefined && <ScoreRing score={scores.seo ?? 0} size={72} label="SEO" />}
        </div>
      )}
      {metrics.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Core Web Vitals</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {metrics.map((m, i) => {
              const colorClass = METRIC_COLORS[m.status as keyof typeof METRIC_COLORS] ?? METRIC_COLORS.info;
              return (
                <div key={i} className="flex items-center justify-between rounded-lg bg-gray-50 border border-gray-100 px-3 py-2">
                  <span className="text-sm text-gray-700">{m.name}</span>
                  <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${colorClass}`}>{m.value}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
