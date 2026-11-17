import { Document, Page, Text, View, Image, StyleSheet } from '@react-pdf/renderer';
import { AnalysisResult, Check } from '../../types';

const styles = StyleSheet.create({
  page: { padding: 40, fontFamily: 'Helvetica', backgroundColor: '#ffffff' },
  coverTitle: { fontSize: 24, fontFamily: 'Helvetica-Bold', color: '#161826', marginTop: 18, marginBottom: 4 },
  coverSubtitle: { fontSize: 11, color: '#75798c', marginBottom: 28 },
  coverUrl: { fontSize: 13, color: '#5d5294', marginBottom: 8 },
  coverDate: { fontSize: 10, color: '#9397ab' },
  scoreBox: { marginTop: 24, borderRadius: 8, padding: 20, backgroundColor: '#f3f5fe', border: '1px solid #e4e7f5', flexDirection: 'row', alignItems: 'center', gap: 16 },
  scoreNum: { fontSize: 48, fontFamily: 'Helvetica-Bold' },
  scoreLabel: { fontSize: 12, color: '#64748b', marginTop: 4 },
  sectionTitle: { fontSize: 16, fontFamily: 'Helvetica-Bold', color: '#161826', marginBottom: 8, marginTop: 20, borderBottom: '1.5px solid #9184d9', paddingBottom: 4 },
  checkRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 8, marginBottom: 5, padding: 6, borderRadius: 4 },
  checkName: { fontSize: 9, fontFamily: 'Helvetica-Bold', color: '#161826' },
  checkValue: { fontSize: 9, color: '#475569' },
  checkRec: { fontSize: 8, color: '#64748b', marginTop: 2 },
  dot: { width: 8, height: 8, borderRadius: 4, marginTop: 2 },
  footer: { position: 'absolute', bottom: 20, left: 40, right: 40, flexDirection: 'row', justifyContent: 'space-between' },
  footerText: { fontSize: 8, color: '#94a3b8' },
  statGrid: { flexDirection: 'row', gap: 8, marginBottom: 10 },
  statBox: { flex: 1, backgroundColor: '#f3f5fe', borderRadius: 6, padding: 8, border: '1px solid #e4e7f5' },
  statLabel: { fontSize: 8, color: '#94a3b8' },
  statValue: { fontSize: 14, fontFamily: 'Helvetica-Bold', color: '#161826', marginTop: 2 },
  scoreRow: { flexDirection: 'row', gap: 10, marginBottom: 10 },
  scoreCard: { flex: 1, alignItems: 'center', backgroundColor: '#f3f5fe', borderRadius: 6, padding: 8, border: '1px solid #e4e7f5' },
  scoreCardNum: { fontSize: 20, fontFamily: 'Helvetica-Bold' },
  scoreCardLabel: { fontSize: 7, color: '#94a3b8', marginTop: 2 },
  metricRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#f3f5fe', borderRadius: 4, padding: 5, marginBottom: 3 },
  metricName: { fontSize: 9, color: '#374151' },
  metricBadge: { fontSize: 8, borderRadius: 3, padding: '2 5' },
  recSection: { marginTop: 16, padding: 12, backgroundColor: '#f5f4ff', border: '1px solid #d2cefd', borderRadius: 6 },
  recTitle: { fontSize: 11, fontFamily: 'Helvetica-Bold', color: '#423a6a', marginBottom: 6 },
  recItem: { fontSize: 9, color: '#2b2741', marginBottom: 4, paddingLeft: 8 },
  promo: { marginTop: 22, padding: 14, backgroundColor: '#f5f4ff', border: '1px solid #d2cefd', borderRadius: 6 },
  promoKicker: { fontSize: 8, color: '#5d5294', marginBottom: 3 },
  promoTitle: { fontSize: 12, fontFamily: 'Helvetica-Bold', color: '#161826', marginBottom: 4 },
  promoText: { fontSize: 9, color: '#3f424d', lineHeight: 1.4 },
});

function scoreColor(s: number) {
  if (s >= 80) return '#16a34a';
  if (s >= 50) return '#ca8a04';
  return '#dc2626';
}

function CheckItem({ check }: { check: Check }) {
  const color = check.status === 'pass' ? '#16a34a' : check.status === 'warning' ? '#ca8a04' : check.status === 'fail' ? '#dc2626' : '#5d5294';
  const bg = check.status === 'pass' ? '#f0fdf4' : check.status === 'warning' ? '#fefce8' : check.status === 'fail' ? '#fef2f2' : '#f5f4ff';
  return (
    <View style={[styles.checkRow, { backgroundColor: bg }]}>
      <View style={[styles.dot, { backgroundColor: color }]} />
      <View style={{ flex: 1 }}>
        <Text style={styles.checkName}>{check.name}{check.value ? ` — ${check.value}` : ''}</Text>
        {check.recommendation && <Text style={styles.checkRec}>{check.recommendation}</Text>}
      </View>
    </View>
  );
}

const LOGO_URL = `${window.location.origin}/run-logo-collage-hell-512.png`;

const FOOTER_BRAND = 'R.U.N. – Rapid URL Navigator · run.dennisrapp.com';

export default function ReportPDF({ data }: { data: AnalysisResult }) {
  const date = new Date(data.analyzed_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  const allRecs = [
    ...data.seo.checks,
    ...data.security.checks,
    ...data.content.checks,
  ].filter(c => c.status === 'fail' || c.status === 'warning').filter(c => c.recommendation);

  return (
    <Document title={`R.U.N. – ${data.url}`} author="R.U.N. – Rapid URL Navigator">
      {/* Cover Page */}
      <Page size="A4" style={styles.page}>
        <Image src={LOGO_URL} style={{ width: 170, height: 78 }} />
        <Text style={styles.coverTitle}>Website-Analyse-Bericht</Text>
        <Text style={styles.coverSubtitle}>Rapid URL Navigator</Text>
        <Text style={styles.coverUrl}>{data.url}</Text>
        <Text style={styles.coverDate}>Analysiert am {date}</Text>

        <View style={styles.scoreBox}>
          <Text style={[styles.scoreNum, { color: scoreColor(data.overall_score) }]}>{data.overall_score}</Text>
          <View>
            <Text style={[styles.scoreLabel, { fontFamily: 'Helvetica-Bold', fontSize: 14, color: scoreColor(data.overall_score) }]}>
              {data.overall_score >= 80 ? 'Gut' : data.overall_score >= 50 ? 'Verbesserungsbedarf' : 'Kritisch'}
            </Text>
            <Text style={styles.scoreLabel}>Gesamt-Score von 100</Text>
          </View>
        </View>

        <View style={[styles.scoreRow, { marginTop: 16 }]}>
          {[
            { label: 'SEO', score: data.seo.score },
            { label: 'Performance', score: data.performance.score ?? 0 },
            { label: 'Sicherheit', score: data.security.score },
            { label: 'Content', score: data.content.score },
          ].map(s => (
            <View key={s.label} style={styles.scoreCard}>
              <Text style={[styles.scoreCardNum, { color: scoreColor(s.score) }]}>{s.score}</Text>
              <Text style={styles.scoreCardLabel}>{s.label}</Text>
            </View>
          ))}
        </View>

        {allRecs.length > 0 && (
          <View style={styles.recSection}>
            <Text style={styles.recTitle}>Wichtigste Empfehlungen</Text>
            {allRecs.slice(0, 8).map((r, i) => (
              <Text key={i} style={styles.recItem}>• {r.recommendation}</Text>
            ))}
          </View>
        )}

        <View style={styles.footer}>
          <Text style={styles.footerText}>{FOOTER_BRAND}</Text>
          <Text style={styles.footerText}>{data.url}</Text>
        </View>
      </Page>

      {/* SEO Page */}
      <Page size="A4" style={styles.page}>
        <Text style={styles.sectionTitle}>SEO-Analyse · Score: {data.seo.score}/100</Text>
        {data.seo.title && (
          <View style={[styles.statGrid, { marginBottom: 10 }]}>
            <View style={styles.statBox}>
              <Text style={styles.statLabel}>Seitentitel</Text>
              <Text style={[styles.statValue, { fontSize: 10 }]}>{data.seo.title}</Text>
            </View>
          </View>
        )}
        {data.seo.checks.map((c, i) => <CheckItem key={i} check={c} />)}
        <View style={styles.footer}>
          <Text style={styles.footerText}>{FOOTER_BRAND}</Text>
          <Text style={styles.footerText}>Seite 2</Text>
        </View>
      </Page>

      {/* Performance Page */}
      <Page size="A4" style={styles.page}>
        <Text style={styles.sectionTitle}>Performance · Score: {data.performance.score ?? '–'}/100</Text>
        {data.performance.scores && (
          <View style={styles.scoreRow}>
            {[
              { label: 'Performance', score: data.performance.scores.performance ?? 0 },
              { label: 'Barrierefreiheit', score: data.performance.scores.accessibility ?? 0 },
              { label: 'Best Practices', score: data.performance.scores.best_practices ?? 0 },
              { label: 'SEO', score: data.performance.scores.seo ?? 0 },
            ].map(s => (
              <View key={s.label} style={styles.scoreCard}>
                <Text style={[styles.scoreCardNum, { color: scoreColor(s.score) }]}>{s.score}</Text>
                <Text style={styles.scoreCardLabel}>{s.label}</Text>
              </View>
            ))}
          </View>
        )}
        {data.performance.metrics.map((m, i) => (
          <View key={i} style={styles.metricRow}>
            <Text style={styles.metricName}>{m.name}</Text>
            <Text style={[styles.metricBadge, {
              backgroundColor: m.status === 'good' ? '#dcfce7' : m.status === 'needs-improvement' ? '#fef9c3' : m.status === 'poor' ? '#fee2e2' : '#f1f5f9',
              color: m.status === 'good' ? '#16a34a' : m.status === 'needs-improvement' ? '#a16207' : m.status === 'poor' ? '#dc2626' : '#64748b',
            }]}>{m.value}</Text>
          </View>
        ))}
        {data.performance.error && <Text style={{ fontSize: 9, color: '#dc2626' }}>{data.performance.error}</Text>}
        <View style={styles.footer}>
          <Text style={styles.footerText}>{FOOTER_BRAND}</Text>
          <Text style={styles.footerText}>Seite 3</Text>
        </View>
      </Page>

      {/* Security & Content Page */}
      <Page size="A4" style={styles.page}>
        <Text style={styles.sectionTitle}>Sicherheit · Score: {data.security.score}/100</Text>
        {data.security.checks.map((c, i) => <CheckItem key={i} check={c} />)}

        <Text style={[styles.sectionTitle, { marginTop: 24 }]}>Content · Score: {data.content.score}/100</Text>
        <View style={[styles.statGrid, { marginBottom: 8 }]}>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Wörter</Text>
            <Text style={styles.statValue}>{data.content.word_count?.toLocaleString('de') ?? '–'}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Lesezeit</Text>
            <Text style={styles.statValue}>{data.content.reading_time_minutes ? `${data.content.reading_time_minutes} Min.` : '–'}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Int. Links</Text>
            <Text style={styles.statValue}>{data.content.internal_links ?? '–'}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Bilder</Text>
            <Text style={styles.statValue}>{data.content.total_images ?? '–'}</Text>
          </View>
        </View>
        {data.content.checks.map((c, i) => <CheckItem key={i} check={c} />)}

        <View style={styles.promo} wrap={false}>
          <Text style={styles.promoKicker}>Dennis Rapp IT-Agency</Text>
          <Text style={styles.promoTitle}>Ich helfe Ihnen, die Schwachstellen Ihrer Website zu beheben.</Text>
          <Text style={styles.promoText}>Sie möchten die Empfehlungen umsetzen lassen? Schreiben Sie mir unverbindlich: info@dennisrapp.com</Text>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>{FOOTER_BRAND}</Text>
          <Text style={styles.footerText}>Seite 4</Text>
        </View>
      </Page>
    </Document>
  );
}
