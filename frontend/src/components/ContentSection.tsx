import { ReactNode } from 'react';
import { ContentResult } from '../types';
import CheckList from './CheckList';
import { BookOpen, Link, Image } from 'lucide-react';

export default function ContentSection({ data }: { data: ContentResult }) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Stat icon={<BookOpen size={14} />} label="Wörter" value={data.word_count?.toLocaleString('de') ?? '–'} />
        <Stat icon={<BookOpen size={14} />} label="Lesezeit" value={data.reading_time_minutes ? `${data.reading_time_minutes} Min.` : '–'} />
        <Stat icon={<Link size={14} />} label="Int. Links" value={data.internal_links?.toString() ?? '–'} />
        <Stat icon={<Image size={14} />} label="Bilder" value={data.total_images?.toString() ?? '–'} />
      </div>
      <CheckList checks={data.checks} />
    </div>
  );
}

function Stat({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="bg-gray-50 border border-gray-100 rounded-lg px-3 py-3 flex flex-col gap-1">
      <div className="flex items-center gap-1 text-gray-400">{icon}<span className="text-xs text-gray-500">{label}</span></div>
      <span className="text-lg font-bold text-gray-800">{value}</span>
    </div>
  );
}
