import { ReactNode } from 'react';
import ScoreRing from './ScoreRing';

interface Props {
  title: string;
  icon: ReactNode;
  score: number | null | undefined;
  error?: string;
  children: ReactNode;
}

export default function SectionCard({ title, icon, score, error, children }: Props) {
  return (
    <section className="card overflow-hidden">
      <div className="flex items-center justify-between px-5 py-4 border-b border-line">
        <div className="flex items-center gap-2.5">
          <span className="text-accent">{icon}</span>
          <h2 className="text-base text-ink">{title}</h2>
        </div>
        {score !== null && score !== undefined && (
          <ScoreRing score={score} size={52} />
        )}
      </div>
      <div className="p-5">
        {error ? (
          <div className="text-sm text-bad bg-bad/10 border border-bad/30 rounded-lg p-3">
            Dieser Bereich konnte nicht geprüft werden: {error}
          </div>
        ) : children}
      </div>
    </section>
  );
}
