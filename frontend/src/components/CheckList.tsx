import { CheckCircle2, AlertTriangle, XCircle, Info } from 'lucide-react';
import { Check } from '../types';

const CONFIG = {
  pass:    { icon: CheckCircle2,  color: 'text-good',       bg: 'bg-good/[0.06]',   border: 'border-good/25',   label: 'Bestanden' },
  warning: { icon: AlertTriangle, color: 'text-warn',       bg: 'bg-warn/[0.07]',   border: 'border-warn/30',   label: 'Warnung' },
  fail:    { icon: XCircle,       color: 'text-bad',        bg: 'bg-bad/[0.08]',    border: 'border-bad/30',    label: 'Fehler' },
  info:    { icon: Info,          color: 'text-accent-400', bg: 'bg-accent/[0.07]', border: 'border-accent/25', label: 'Hinweis' },
} as const;

export default function CheckList({ checks }: { checks: Check[] }) {
  return (
    <ul className="space-y-2">
      {checks.map((c, i) => {
        const cfg = CONFIG[c.status];
        const Icon = cfg.icon;
        return (
          <li key={i} className={`flex items-start gap-3 rounded-lg p-3 border ${cfg.bg} ${cfg.border}`}>
            <Icon size={16} className={`mt-0.5 shrink-0 ${cfg.color}`} aria-label={cfg.label} />
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-baseline gap-x-2">
                <span className="text-sm text-ink">{c.name}</span>
                {c.value && <span className={`text-xs break-all ${cfg.color}`}>{c.value}</span>}
              </div>
              {c.recommendation && (
                <p className="mt-0.5 text-xs text-neutral-400">{c.recommendation}</p>
              )}
            </div>
          </li>
        );
      })}
    </ul>
  );
}
