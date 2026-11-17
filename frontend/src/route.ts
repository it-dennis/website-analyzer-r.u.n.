import { useEffect, useState } from 'react';

export type Page = 'home' | 'impressum' | 'datenschutz';

function pageFromPath(path: string): Page {
  const p = path.replace(/\/+$/, '');
  if (p === '/impressum') return 'impressum';
  if (p === '/datenschutz') return 'datenschutz';
  return 'home';
}

/** Minimale Pfad-Navigation ohne Router-Bibliothek: /impressum und /datenschutz sind echte URLs.
 *  Der Server liefert für jeden Pfad index.html aus (try_files). */
export function usePage(): [Page, (to: string) => void] {
  const [page, setPage] = useState<Page>(() => pageFromPath(window.location.pathname));

  useEffect(() => {
    const onPop = () => setPage(pageFromPath(window.location.pathname));
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  function navigate(to: string) {
    window.history.pushState({}, '', to);
    setPage(pageFromPath(to));
    window.scrollTo({ top: 0 });
  }

  return [page, navigate];
}
