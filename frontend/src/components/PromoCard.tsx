import { useEffect, useState } from 'react';
import { ArrowRight, Check } from 'lucide-react';

interface Promo {
  brand: string;
  kicker: string;
  headline: string;
  text: string;
  points: string[];
  cta: { label: string; href: string };
}

// Fallback, falls /promo/promo.json nicht geladen werden kann.
const DEFAULT_PROMO: Promo = {
  brand: 'Dennis Rapp IT-Agency',
  kicker: 'Ihre Website, professionell verbessert',
  headline: 'Ihre Webseite hat Aua?',
  text: 'Jetzt unverbindlich anfragen!',
  points: [],
  cta: { label: 'Jetzt anfragen', href: 'https://dennisrapp.com' },
};

function usePromo(): Promo {
  const [promo, setPromo] = useState<Promo>(DEFAULT_PROMO);
  useEffect(() => {
    let cancelled = false;
    fetch('/promo/promo.json', { cache: 'no-cache' })
      .then(r => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((p: Partial<Promo>) => {
        if (!cancelled && p && p.headline && p.cta?.href) setPromo({ ...DEFAULT_PROMO, ...p, cta: { ...DEFAULT_PROMO.cta, ...p.cta } });
      })
      .catch(() => { /* Fallback bleibt */ });
    return () => { cancelled = true; };
  }, []);
  return promo;
}

/** Werbefläche der Dennis Rapp IT-Agency. Inhalt: frontend/public/promo/promo.json (ohne Neubau änderbar).
 *  Im Link steht {url} für die geprüfte Adresse. */
export default function PromoCard({ scannedUrl }: { scannedUrl?: string }) {
  const promo = usePromo();
  const href = promo.cta.href.replace('{url}', encodeURIComponent(scannedUrl ?? ''));
  // Externe Seiten in neuem Tab, damit das Ergebnis der Analyse nicht verloren geht.
  const external = /^https?:\/\//i.test(href);

  return (
    <aside className="card relative overflow-hidden" aria-label="Angebot der Dennis Rapp IT-Agency">
      <div className="absolute inset-y-0 left-0 w-px bg-gradient-to-b from-transparent via-accent to-transparent" aria-hidden />
      <div className="grid gap-6 p-6 md:grid-cols-[1fr_auto] md:items-center">
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <img src="/agency-icon.png" width={32} height={32} alt="" className="rounded-md" />
            <div className="leading-tight">
              <p className="text-xs text-accent-300">{promo.kicker}</p>
              <p className="text-xs text-neutral-500">{promo.brand}</p>
            </div>
          </div>
          <h2 className="text-lg text-ink max-w-xl">{promo.headline}</h2>
          <p className="text-sm text-neutral-400 max-w-xl">{promo.text}</p>
          {promo.points?.length > 0 && (
            <ul className="flex flex-wrap gap-x-5 gap-y-1.5 pt-1">
              {promo.points.map(p => (
                <li key={p} className="flex items-center gap-1.5 text-xs text-neutral-300">
                  <Check size={13} className="text-accent shrink-0" /> {p}
                </li>
              ))}
            </ul>
          )}
        </div>
        <a href={href} className="btn btn-primary whitespace-nowrap" {...(external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}>
          {promo.cta.label} <ArrowRight size={16} />
        </a>
      </div>
    </aside>
  );
}
