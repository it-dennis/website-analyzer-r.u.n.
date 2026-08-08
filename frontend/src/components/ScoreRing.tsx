interface Props {
  score: number;
  size?: number;
  label?: string;
}

function scoreColor(s: number) {
  if (s >= 80) return { stroke: '#22c55e', text: 'text-green-600' };
  if (s >= 50) return { stroke: '#eab308', text: 'text-yellow-600' };
  return { stroke: '#ef4444', text: 'text-red-600' };
}

export default function ScoreRing({ score, size = 80, label }: Props) {
  const r = (size - 10) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  const { stroke, text } = scoreColor(score);

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#e5e7eb" strokeWidth={8} />
        <circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none"
          stroke={stroke}
          strokeWidth={8}
          strokeDasharray={circ}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
        <text x="50%" y="50%" dominantBaseline="middle" textAnchor="middle" fontSize={size < 80 ? 14 : 20} fontWeight="700" fill={stroke}>
          {score}
        </text>
      </svg>
      {label && <span className={`text-xs font-medium ${text}`}>{label}</span>}
    </div>
  );
}
