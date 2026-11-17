interface Props {
  score: number;
  size?: number;
  label?: string;
}

function scoreColor(s: number) {
  if (s >= 80) return { stroke: '#7ccf9a', text: 'text-good' };
  if (s >= 50) return { stroke: '#e6bd6f', text: 'text-warn' };
  return { stroke: '#ee8a8a', text: 'text-bad' };
}

export default function ScoreRing({ score, size = 80, label }: Props) {
  const r = (size - 10) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  const { stroke, text } = scoreColor(score);

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} role="img" aria-label={`${label ?? 'Score'} ${score} von 100`}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(233,233,237,0.1)" strokeWidth={8} />
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
        <text x="50%" y="50%" dominantBaseline="middle" textAnchor="middle" fontSize={size < 80 ? 14 : 22} fontWeight="500" fill={stroke}>
          {score}
        </text>
      </svg>
      {label && <span className={`text-xs ${text}`}>{label}</span>}
    </div>
  );
}
