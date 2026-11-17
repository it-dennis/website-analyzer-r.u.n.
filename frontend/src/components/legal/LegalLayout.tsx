import { ReactNode } from 'react';

export function LegalLayout({ title, children }: { title: string; children: ReactNode }) {
  return (
    <article className="max-w-3xl space-y-8 pb-8">
      <h1 className="text-3xl text-ink">{title}</h1>
      {children}
    </article>
  );
}

export function LegalSection({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="space-y-3 text-sm leading-relaxed text-neutral-300">
      <h2 className="text-lg text-ink">{title}</h2>
      {children}
    </section>
  );
}

export function LegalSub({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="space-y-2">
      <h3 className="text-sm text-ink">{title}</h3>
      {children}
    </div>
  );
}

export function Address({ children }: { children: ReactNode }) {
  return <address className="not-italic rounded-lg border border-line bg-surface px-4 py-3 leading-relaxed">{children}</address>;
}

export function List({ items }: { items: ReactNode[] }) {
  return (
    <ul className="list-disc space-y-1 pl-5 marker:text-accent">
      {items.map((it, i) => <li key={i}>{it}</li>)}
    </ul>
  );
}
