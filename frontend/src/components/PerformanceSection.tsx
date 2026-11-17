import { PerformanceResult } from '../types';
import ScoreRing from './ScoreRing';

const METRIC_COLORS = {
  good: 'bg-good/15 text-good',
  'needs-improvement': 'bg-warn/15 text-warn',
  poor: 'bg-bad/15 text-bad',
  info: 'bg-white/10 text-neutral-300',
};

export default function PerformanceSection({ data }: { data: PerformanceResult }) {
  const { scores, metrics, error } = data;

  if (error) {
    return (
      <div className="text-sm text-warn bg-warn/10 border border-warn/30 rounded-lg p-3">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {scores && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {scores.performance != null && <ScoreRing score={scores.performance} size={72} label="Performance" />}
          {scores.accessibility != null && <ScoreRing score={scores.accessibility} size={72} label="Barrierefreiheit" />}
          {scores.best_practices != null && <ScoreRing score={scores.best_practices} size={72} label="Best Practices" />}
          {scores.seo != null && <ScoreRing score={scores.seo} size={72} label="SEO" />}
        </div>
      )}
      {metrics.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-xs text-neutral-500 uppercase tracking-wider">Core Web Vitals (mobil)</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {metrics.map((m, i) => {
              const colorClass = METRIC_COLORS[m.status as keyof typeof METRIC_COLORS] ?? METRIC_COLORS.info;
              return (
                <div key={i} className="flex items-center justify-between gap-2 rounded-lg bg-bg/60 border border-line px-3 py-2">
                  <span className="text-sm text-neutral-300">{m.name}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full whitespace-nowrap ${colorClass}`}>{m.value}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
