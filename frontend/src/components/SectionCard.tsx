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
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <span className="text-gray-500">{icon}</span>
          <h2 className="text-base font-semibold text-gray-800">{title}</h2>
        </div>
        {score !== null && score !== undefined && (
          <ScoreRing score={score} size={52} />
        )}
      </div>
      <div className="p-5">
        {error ? (
          <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">
            Fehler: {error}
          </div>
        ) : children}
      </div>
    </div>
  );
}
