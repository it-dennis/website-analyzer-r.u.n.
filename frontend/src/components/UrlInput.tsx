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
    <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 w-full">
      <label htmlFor="url" className="sr-only">Adresse der Website</label>
      <input
        id="url"
        type="text"
        inputMode="url"
        autoComplete="url"
        value={url}
        onChange={e => setUrl(e.target.value)}
        placeholder="www.ihre-website.de"
        className="flex-1 min-w-0 px-4 py-3 rounded-lg border border-line bg-surface text-ink placeholder:text-neutral-600 text-sm hover:border-accent-700 transition-colors"
        disabled={loading}
      />
      <button type="submit" disabled={loading || !url.trim()} className="btn btn-primary px-6 py-3">
        {loading ? (
          <><Loader2 size={16} className="animate-spin" /> Analysiere …</>
        ) : (
          <><Search size={16} /> Website prüfen</>
        )}
      </button>
    </form>
  );
}
