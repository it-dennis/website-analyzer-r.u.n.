import { useState } from 'react';
import { pdf } from '@react-pdf/renderer';
import { FileDown, FileText, Loader2 } from 'lucide-react';
import { AnalysisResult } from '../types';
import ReportPDF from './pdf/ReportPDF';

function generateMarkdown(data: AnalysisResult): string {
  const date = new Date(data.analyzed_at).toLocaleDateString('de-DE');
  const scoreLabel = (s: number) => s >= 80 ? '✅ Gut' : s >= 50 ? '⚠️ Mittel' : '❌ Kritisch';

  const checks = (items: AnalysisResult['seo']['checks']) =>
    items.map(c => {
      const icon = c.status === 'pass' ? '✅' : c.status === 'warning' ? '⚠️' : c.status === 'fail' ? '❌' : 'ℹ️';
      const rec = c.recommendation ? `\n  > 💡 ${c.recommendation}` : '';
      return `- ${icon} **${c.name}**${c.value ? `: ${c.value}` : ''}${rec}`;
    }).join('\n');

  return `# R.U.N.-Bericht: ${data.url}

**Analysiert am:** ${date}
**Gesamt-Score:** ${data.overall_score}/100 ${scoreLabel(data.overall_score)}

---

## Scores im Überblick

| Bereich | Score |
|---------|-------|
| SEO | ${data.seo.score}/100 ${scoreLabel(data.seo.score)} |
| Performance | ${data.performance.score ?? 'N/A'}/100 ${data.performance.score !== undefined ? scoreLabel(data.performance.score) : ''} |
| Sicherheit | ${data.security.score}/100 ${scoreLabel(data.security.score)} |
| Content | ${data.content.score}/100 ${scoreLabel(data.content.score)} |

---

## SEO-Analyse

${checks(data.seo.checks)}

---

## Performance

${data.performance.error ? `> ⚠️ ${data.performance.error}` : ''}
${data.performance.scores ? `
| Kategorie | Score |
|-----------|-------|
| Performance | ${data.performance.scores.performance ?? '–'} |
| Accessibility | ${data.performance.scores.accessibility ?? '–'} |
| Best Practices | ${data.performance.scores.best_practices ?? '–'} |
| SEO | ${data.performance.scores.seo ?? '–'} |
` : ''}
${data.performance.metrics.length > 0 ? '### Core Web Vitals\n\n' + data.performance.metrics.map(m => `- **${m.name}:** ${m.value}`).join('\n') : ''}

---

## Sicherheit

${checks(data.security.checks)}

---

## Content

- **Wortanzahl:** ${data.content.word_count?.toLocaleString('de') ?? '–'}
- **Lesezeit:** ${data.content.reading_time_minutes ? `${data.content.reading_time_minutes} Minuten` : '–'}
- **Interne Links:** ${data.content.internal_links ?? '–'}
- **Externe Links:** ${data.content.external_links ?? '–'}
- **Bilder gesamt:** ${data.content.total_images ?? '–'}
- **Bilder ohne Alt-Text:** ${data.content.images_missing_alt ?? '–'}

${checks(data.content.checks)}

---

## Handlungsempfehlungen

${[...data.seo.checks, ...data.security.checks, ...data.content.checks]
  .filter(c => (c.status === 'fail' || c.status === 'warning') && c.recommendation)
  .map((c, i) => `${i + 1}. **${c.name}:** ${c.recommendation}`)
  .join('\n')}

---

*Erstellt mit R.U.N. – Rapid URL Navigator*
`;
}

interface Props {
  data: AnalysisResult;
}

export default function ExportBar({ data }: Props) {
  const [pdfLoading, setPdfLoading] = useState(false);

  async function downloadPdf() {
    setPdfLoading(true);
    try {
      const blob = await pdf(<ReportPDF data={data} />).toBlob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `run-${new URL(data.url).hostname}-${new Date().toISOString().slice(0, 10)}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setPdfLoading(false);
    }
  }

  function downloadMarkdown() {
    const md = generateMarkdown(data);
    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `run-${new URL(data.url).hostname}-${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="flex flex-wrap gap-3 justify-end">
      <button
        onClick={downloadMarkdown}
        className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <FileText size={15} />
        Markdown
      </button>
      <button
        onClick={downloadPdf}
        disabled={pdfLoading}
        className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
      >
        {pdfLoading ? <Loader2 size={15} className="animate-spin" /> : <FileDown size={15} />}
        PDF-Bericht
      </button>
    </div>
  );
}
