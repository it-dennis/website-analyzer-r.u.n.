import { CheckCircle2, AlertTriangle, XCircle, Info } from 'lucide-react';
import { Check } from '../types';

const CONFIG = {
  pass:    { icon: CheckCircle2, color: 'text-green-600',  bg: 'bg-green-50',  border: 'border-green-200' },
  warning: { icon: AlertTriangle, color: 'text-yellow-600', bg: 'bg-yellow-50', border: 'border-yellow-200' },
  fail:    { icon: XCircle,      color: 'text-red-600',    bg: 'bg-red-50',    border: 'border-red-200' },
  info:    { icon: Info,         color: 'text-blue-600',   bg: 'bg-blue-50',   border: 'border-blue-200' },
} as const;

export default function CheckList({ checks }: { checks: Check[] }) {
  return (
    <ul className="space-y-2">
      {checks.map((c, i) => {
        const cfg = CONFIG[c.status];
        const Icon = cfg.icon;
        return (
          <li key={i} className={`flex items-start gap-3 rounded-lg p-3 border ${cfg.bg} ${cfg.border}`}>
            <Icon size={16} className={`mt-0.5 shrink-0 ${cfg.color}`} />
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-baseline gap-x-2">
                <span className="text-sm font-medium text-gray-800">{c.name}</span>
                {c.value && <span className={`text-xs ${cfg.color}`}>{c.value}</span>}
              </div>
              {c.recommendation && (
                <p className="mt-0.5 text-xs text-gray-600">{c.recommendation}</p>
              )}
            </div>
          </li>
        );
      })}
    </ul>
  );
}
