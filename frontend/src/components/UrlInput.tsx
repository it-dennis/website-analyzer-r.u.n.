import { useState, FormEvent } from 'react';
import { Search, Loader2 } from 'lucide-react';

interface Props {
  onSubmit: (url: string) => void;
  loading: boolean;
  initialValue?: string;
}

export default function UrlInput({ onSubmit, loading, initialValue = '' }: Props) {
  const [url, setUrl] = useState(initialValue);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = url.trim();
    if (trimmed) onSubmit(trimmed);
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 w-full max-w-2xl mx-auto">
      <input
        type="text"
        value={url}
        onChange={e => setUrl(e.target.value)}
        placeholder="z.B. www.denira-entertainment.com"
        className="flex-1 px-4 py-3 rounded-lg border border-gray-300 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading || !url.trim()}
        className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
      >
        {loading ? (
          <><Loader2 size={16} className="animate-spin" /> Analysiere…</>
        ) : (
          <><Search size={16} /> Analysieren</>
        )}
      </button>
    </form>
  );
}
