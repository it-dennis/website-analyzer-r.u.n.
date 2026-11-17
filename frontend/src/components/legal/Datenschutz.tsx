import { LegalLayout, LegalSection, LegalSub, Address, List } from './LegalLayout';

export default function Datenschutz() {
  return (
    <LegalLayout title="Datenschutzerklärung">
      <LegalSection title="1. Verantwortlicher">
        <p>
          Verantwortlicher im Sinne der Datenschutz-Grundverordnung (DSGVO) und anderer nationaler Datenschutzgesetze der Mitgliedstaaten sowie sonstiger datenschutzrechtlicher Bestimmungen ist:
        </p>
        <Address>
          Dennis Rapp IT-Agency<br />
          Dennis Rapp<br />
          In den Fischergärten 8<br />
          72074 Tübingen<br />
          Deutschland<br />
          Telefon: +49 1575 8547319<br />
          E-Mail: info@dennisrapp.com<br />
          Web: www.dennisrapp.com
        </Address>
      </LegalSection>

      <LegalSection title="2. Allgemeine Hinweise zur Datenverarbeitung">
        <LegalSub title="Umfang der Verarbeitung personenbezogener Daten">
          <p>
            Ich verarbeite personenbezogene Daten meiner Nutzer grundsätzlich nur, soweit dies zur Bereitstellung einer funktionsfähigen Website sowie meiner Inhalte und Leistungen erforderlich ist. Die Verarbeitung personenbezogener Daten erfolgt regelmäßig nur nach Einwilligung der Nutzerin oder des Nutzers. Eine Ausnahme gilt in solchen Fällen, in denen eine vorherige Einholung einer Einwilligung aus tatsächlichen Gründen nicht möglich ist und die Verarbeitung der Daten durch gesetzliche Vorschriften gestattet ist.
          </p>
        </LegalSub>
        <LegalSub title="Rechtsgrundlagen">
          <List items={[
            'Art. 6 Abs. 1 lit. a DSGVO – Einwilligung der betroffenen Person',
            'Art. 6 Abs. 1 lit. b DSGVO – Verarbeitung zur Erfüllung eines Vertrags oder zur Durchführung vorvertraglicher Maßnahmen',
            'Art. 6 Abs. 1 lit. c DSGVO – Erfüllung rechtlicher Verpflichtungen',
            'Art. 6 Abs. 1 lit. f DSGVO – Wahrung berechtigter Interessen, sofern nicht die Interessen oder Grundrechte der betroffenen Person überwiegen',
          ]} />
        </LegalSub>
        <LegalSub title="Datenlöschung und Speicherdauer">
          <p>
            Die personenbezogenen Daten der betroffenen Person werden gelöscht oder gesperrt, sobald der Zweck der Speicherung entfällt. Eine Speicherung kann darüber hinaus erfolgen, wenn dies durch den europäischen oder nationalen Gesetzgeber in unionsrechtlichen Verordnungen, Gesetzen oder sonstigen Vorschriften, denen der Verantwortliche unterliegt, vorgesehen wurde – beispielsweise handels- und steuerrechtliche Aufbewahrungsfristen (regelmäßig 6 bzw. 10 Jahre).
          </p>
        </LegalSub>
      </LegalSection>

      <LegalSection title="3. Was R.U.N. mit Ihren Eingaben macht">
        <p>
          R.U.N. (Rapid URL Navigator) ist ein kostenloses Werkzeug zur technischen Analyse von Websites. Eine Anmeldung oder ein Benutzerkonto ist nicht nötig.
        </p>
        <LegalSub title="Eingegebene Website-Adresse">
          <p>
            Wenn Sie eine Adresse eingeben und die Analyse starten, übermittelt Ihr Browser diese Adresse an meinen Server. Der Server ruft die angegebene Website ab (dabei erscheint der Name „WebCheckAnalyzer“ als Absender), prüft Inhalt, Sicherheitsmerkmale, Weiterleitungen und Zertifikat und stellt das Ergebnis in Ihrem Browser dar. Die eingegebene Adresse und das Ergebnis werden nicht dauerhaft gespeichert. Sie werden nur für die Dauer der Analyse im Arbeitsspeicher verarbeitet. PDF- und Markdown-Berichte werden ausschließlich in Ihrem Browser erzeugt.
          </p>
          <p>
            Bitte geben Sie nur Adressen öffentlich erreichbarer Websites ein, nicht solche mit Zugangsdaten in der Adresse. Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO (Bereitstellung der angefragten Analyse) bzw. Art. 6 Abs. 1 lit. f DSGVO.
          </p>
        </LegalSub>
        <LegalSub title="Messung der Ladezeit durch Google PageSpeed Insights">
          <p>
            Für die Performance-Messung übermittelt mein Server die eingegebene Website-Adresse an die PageSpeed-Insights-API von Google LLC, 1600 Amphitheatre Parkway, Mountain View, CA 94043, USA. Google ruft die Website selbst ab und liefert Messwerte zurück. Ihre IP-Adresse wird dabei nicht an Google weitergegeben, da die Anfrage von meinem Server ausgeht. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an einer zuverlässigen Messung). Google LLC ist nach dem EU-US Data Privacy Framework zertifiziert. Informationen: policies.google.com/privacy.
          </p>
        </LegalSub>
        <LegalSub title="Begrenzung der Anfragen (Missbrauchsschutz)">
          <p>
            Um Missbrauch und Überlastung zu verhindern, zählt der Server die Anfragen je IP-Adresse. Die IP-Adresse wird dafür ausschließlich im Arbeitsspeicher gehalten und nach höchstens etwa einer Stunde ohne weitere Anfrage verworfen. Beim Neustart des Dienstes wird der Speicher geleert. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO (Sicherheit und Verfügbarkeit des Dienstes).
          </p>
        </LegalSub>
      </LegalSection>

      <LegalSection title="4. Bereitstellung der Website und Server-Protokolle">
        <p>
          Beim Aufruf dieser Website verarbeitet der Server technisch notwendige Verbindungsdaten, insbesondere Ihre IP-Adresse, um die Seite auszuliefern. Für R.U.N. werden keine Zugriffsprotokolle mit IP-Adressen geführt. Technische Fehlerprotokolle des Servers können im Störungsfall Verbindungsdaten enthalten und werden nur so lange aufbewahrt, wie es für die Fehlersuche und die IT-Sicherheit erforderlich ist. Eine Zusammenführung mit anderen Datenquellen erfolgt nicht. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO; das berechtigte Interesse besteht in der technischen Bereitstellung und IT-Sicherheit.
        </p>
      </LegalSection>

      <LegalSection title="5. Hosting">
        <p>
          Diese Website wird auf einem virtuellen Server der netcup GmbH in einem Rechenzentrum innerhalb der Europäischen Union (Deutschland) betrieben. Mit dem Hosting-Anbieter besteht ein Vertrag zur Auftragsverarbeitung nach Art. 28 DSGVO. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO.
        </p>
      </LegalSection>

      <LegalSection title="6. Schriftarten">
        <p>
          Die auf dieser Website verwendete Schriftart (Inter) wird lokal vom eigenen Server ausgeliefert. Es findet keine Verbindung zu Google Fonts oder anderen Schriftdiensten statt.
        </p>
      </LegalSection>

      <LegalSection title="7. Cookies und lokale Speicherung">
        <p>
          R.U.N. setzt keine Cookies und speichert keine Daten in Ihrem Browser. Es werden keine Tracking-, Marketing- oder Analyse-Werkzeuge eingesetzt. Eine Einwilligungsabfrage (Cookie-Banner) ist deshalb nicht nötig.
        </p>
      </LegalSection>

      <LegalSection title="8. Kontaktaufnahme">
        <p>
          Wenn Sie über das Angebot der Dennis Rapp IT-Agency per E-Mail oder Telefon Kontakt aufnehmen, werden Ihre Angaben (Name, E-Mail-Adresse, Telefonnummer, Inhalt der Nachricht, ggf. die analysierte Website-Adresse) zum Zweck der Bearbeitung der Anfrage und für den Fall von Anschlussfragen gespeichert. Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO (Anbahnung / Erfüllung eines Vertrags) bzw. Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an der Beantwortung). Die Daten werden gelöscht, sobald sie für den Zweck ihrer Erhebung nicht mehr erforderlich sind, sofern keine gesetzlichen Aufbewahrungspflichten entgegenstehen.
        </p>
      </LegalSection>

      <LegalSection title="9. Auftragsverarbeitung und Empfänger">
        <p>
          Im Rahmen meiner Tätigkeit als IT-Dienstleister kann es erforderlich sein, externe Dienstleister einzubinden (z. B. Hosting-Provider, Domain-Registrare). Diese werden ausschließlich auf Grundlage eines Auftragsverarbeitungsvertrages nach Art. 28 DSGVO eingesetzt. Eine Übermittlung in Drittländer erfolgt nur, sofern ein angemessenes Schutzniveau gemäß Art. 44 ff. DSGVO sichergestellt ist (z. B. Angemessenheitsbeschluss oder EU-Standardvertragsklauseln).
        </p>
      </LegalSection>

      <LegalSection title="10. Rechte der betroffenen Person">
        <p>Sie haben gegenüber dem Verantwortlichen folgende Rechte hinsichtlich der Sie betreffenden personenbezogenen Daten:</p>
        <List items={[
          'Recht auf Auskunft (Art. 15 DSGVO)',
          'Recht auf Berichtigung (Art. 16 DSGVO)',
          'Recht auf Löschung (Art. 17 DSGVO)',
          'Recht auf Einschränkung der Verarbeitung (Art. 18 DSGVO)',
          'Recht auf Datenübertragbarkeit (Art. 20 DSGVO)',
          'Widerspruchsrecht (Art. 21 DSGVO)',
          'Recht auf Widerruf einer erteilten Einwilligung (Art. 7 Abs. 3 DSGVO) mit Wirkung für die Zukunft',
        ]} />
        <p>Zur Ausübung Ihrer Rechte genügt eine formlose Mitteilung an die oben genannten Kontaktdaten.</p>
      </LegalSection>

      <LegalSection title="11. Beschwerderecht bei der Aufsichtsbehörde">
        <p>
          Unbeschadet eines anderweitigen verwaltungsrechtlichen oder gerichtlichen Rechtsbehelfs steht Ihnen das Recht auf Beschwerde bei einer Aufsichtsbehörde zu, insbesondere im Mitgliedstaat Ihres Aufenthaltsorts, Ihres Arbeitsplatzes oder des Orts des mutmaßlichen Verstoßes.
        </p>
        <Address>
          Zuständige Aufsichtsbehörde:<br />
          Der Landesbeauftragte für den Datenschutz und die Informationsfreiheit Baden-Württemberg<br />
          Lautenschlagerstraße 20<br />
          70173 Stuttgart<br />
          www.baden-wuerttemberg.datenschutz.de
        </Address>
      </LegalSection>

      <LegalSection title="12. Datensicherheit">
        <p>
          Diese Website nutzt aus Gründen der Sicherheit und zum Schutz der Übertragung vertraulicher Inhalte eine SSL-/TLS-Verschlüsselung. Eine verschlüsselte Verbindung erkennen Sie an der Adresszeile des Browsers (https://) und am Schloss-Symbol.
        </p>
      </LegalSection>

      <LegalSection title="13. Aktualität und Änderung dieser Datenschutzerklärung">
        <p>
          Durch die Weiterentwicklung der Website oder aufgrund geänderter gesetzlicher Vorgaben kann es notwendig werden, diese Datenschutzerklärung anzupassen. Die jeweils aktuelle Datenschutzerklärung kann jederzeit auf dieser Seite abgerufen werden.
        </p>
        <p className="text-xs text-neutral-500">Stand: November 2026</p>
      </LegalSection>
    </LegalLayout>
  );
}
