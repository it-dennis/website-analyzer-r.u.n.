import { Document, Page, Text, View, StyleSheet } from '@react-pdf/renderer';
import { AnalysisResult, Check } from '../../types';

const styles = StyleSheet.create({
  page: { padding: 40, fontFamily: 'Helvetica', backgroundColor: '#ffffff' },
  coverTitle: { fontSize: 28, fontFamily: 'Helvetica-Bold', color: '#1e3a5f', marginBottom: 4 },
  coverSubtitle: { fontSize: 11, color: '#64748b', marginBottom: 32 },
  coverUrl: { fontSize: 13, color: '#2563eb', marginBottom: 8 },
  coverDate: { fontSize: 10, color: '#94a3b8' },
  scoreBox: { marginTop: 24, borderRadius: 8, padding: 20, backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', flexDirection: 'row', alignItems: 'center', gap: 16 },
  scoreNum: { fontSize: 48, fontFamily: 'Helvetica-Bold' },
  scoreLabel: { fontSize: 12, color: '#64748b', marginTop: 4 },
  sectionTitle: { fontSize: 16, fontFamily: 'Helvetica-Bold', color: '#1e293b', marginBottom: 8, marginTop: 20, borderBottom: '1px solid #e2e8f0', paddingBottom: 4 },
  checkRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 8, marginBottom: 5, padding: 6, borderRadius: 4 },
  checkName: { fontSize: 9, fontFamily: 'Helvetica-Bold', color: '#1e293b' },
  checkValue: { fontSize: 9, color: '#475569' },
  checkRec: { fontSize: 8, color: '#64748b', marginTop: 2 },
  dot: { width: 8, height: 8, borderRadius: 4, marginTop: 2 },
  footer: { position: 'absolute', bottom: 20, left: 40, right: 40, flexDirection: 'row', justifyContent: 'space-between' },
  footerText: { fontSize: 8, color: '#94a3b8' },
  statGrid: { flexDirection: 'row', gap: 8, marginBottom: 10 },
  statBox: { flex: 1, backgroundColor: '#f8fafc', borderRadius: 6, padding: 8, border: '1px solid #e2e8f0' },
  statLabel: { fontSize: 8, color: '#94a3b8' },
  statValue: { fontSize: 14, fontFamily: 'Helvetica-Bold', color: '#1e293b', marginTop: 2 },
  scoreRow: { flexDirection: 'row', gap: 10, marginBottom: 10 },
  scoreCard: { flex: 1, alignItems: 'center', backgroundColor: '#f8fafc', borderRadius: 6, padding: 8, border: '1px solid #e2e8f0' },
  scoreCardNum: { fontSize: 20, fontFamily: 'Helvetica-Bold' },
  scoreCardLabel: { fontSize: 7, color: '#94a3b8', marginTop: 2 },
  metricRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#f8fafc', borderRadius: 4, padding: 5, marginBottom: 3 },
  metricName: { fontSize: 9, color: '#374151' },
  metricBadge: { fontSize: 8, borderRadius: 3, padding: '2 5' },
  recSection: { marginTop: 16, padding: 12, backgroundColor: '#fffbeb', border: '1px solid #fde68a', borderRadius: 6 },
  recTitle: { fontSize: 11, fontFamily: 'Helvetica-Bold', color: '#92400e', marginBottom: 6 },
  recItem: { fontSize: 9, color: '#78350f', marginBottom: 4, paddingLeft: 8 },
});

function scoreColor(s: number) {
  if (s >= 80) return '#16a34a';
  if (s >= 50) return '#ca8a04';
  return '#dc2626';
}

function CheckItem({ check }: { check: Check }) {
  const color = check.status === 'pass' ? '#16a34a' : check.status === 'warning' ? '#ca8a04' : check.status === 'fail' ? '#dc2626' : '#2563eb';
  const bg = check.status === 'pass' ? '#f0fdf4' : check.status === 'warning' ? '#fefce8' : check.status === 'fail' ? '#fef2f2' : '#eff6ff';
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

export default function ReportPDF({ data }: { data: AnalysisResult }) {
  const date = new Date(data.analyzed_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  const allRecs = [
    ...data.seo.checks,
    ...data.security.checks,
    ...data.content.checks,
  ].filter(c => c.status === 'fail' || c.status === 'warning').filter(c => c.recommendation);

  return (
    <Document title={`R.U.N. – ${data.url}`} author="R.U.N. Analyzer">
      {/* Cover Page */}
      <Page size="A4" style={styles.page}>
        <Text style={styles.coverTitle}>R.U.N.</Text>
        <Text style={styles.coverSubtitle}>Website-Analyse-Bericht</Text>
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
          <Text style={styles.footerText}>R.U.N. Analyzer</Text>
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
          <Text style={styles.footerText}>R.U.N. – SEO</Text>
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
              { label: 'Accessibility', score: data.performance.scores.accessibility ?? 0 },
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
          <Text style={styles.footerText}>R.U.N. – Performance</Text>
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

        <View style={styles.footer}>
          <Text style={styles.footerText}>R.U.N. Analyzer</Text>
          <Text style={styles.footerText}>Seite 4</Text>
        </View>
      </Page>
    </Document>
  );
}
