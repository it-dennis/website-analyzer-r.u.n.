import { LegalLayout, LegalSection, Address } from './LegalLayout';

export default function Impressum() {
  return (
    <LegalLayout title="Impressum">
      <LegalSection title="Diensteanbieter">
        <Address>
          Dennis Rapp IT-Agency<br />
          Inhaber: Dennis Rapp<br />
          In den Fischergärten 8<br />
          72074 Tübingen<br />
          Deutschland
        </Address>
      </LegalSection>

      <LegalSection title="Kontakt">
        <p>
          Telefon: +49 1575 8547319<br />
          E-Mail: <a className="text-accent-300 underline underline-offset-2 hover:text-accent-200" href="mailto:info@dennisrapp.com">info@dennisrapp.com</a><br />
          Web: www.dennisrapp.com
        </p>
      </LegalSection>

      <LegalSection title="Umsatzsteuer-Identifikationsnummer">
        <p>
          Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz: wird auf Anfrage mitgeteilt bzw. nach Erteilung hier ergänzt.
        </p>
        <p>
          Hinweis nach § 19 UStG: Sofern als Kleinunternehmer geführt, wird gemäß § 19 UStG keine Umsatzsteuer berechnet.
        </p>
      </LegalSection>

      <LegalSection title="Redaktionell verantwortlich">
        <p>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV:</p>
        <Address>
          Dennis Rapp<br />
          In den Fischergärten 8<br />
          72074 Tübingen
        </Address>
      </LegalSection>

      <LegalSection title="Verbraucherstreitbeilegung">
        <p>
          Ich bin nicht bereit und nicht verpflichtet, an einem Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.
        </p>
      </LegalSection>

      <LegalSection title="Haftung für Inhalte">
        <p>
          Als Diensteanbieter bin ich gemäß § 7 Abs. 1 DDG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 DDG bin ich als Diensteanbieter jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen.
        </p>
        <p>
          Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt. Eine diesbezügliche Haftung ist jedoch erst ab dem Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung möglich. Bei Bekanntwerden entsprechender Rechtsverletzungen werde ich diese Inhalte umgehend entfernen.
        </p>
      </LegalSection>

      <LegalSection title="Haftung für Links">
        <p>
          Dieses Angebot enthält Links zu externen Webseiten Dritter, auf deren Inhalte ich keinen Einfluss habe. Deshalb kann ich für diese fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich. Die verlinkten Seiten wurden zum Zeitpunkt der Verlinkung auf mögliche Rechtsverstöße überprüft. Rechtswidrige Inhalte waren zum Zeitpunkt der Verlinkung nicht erkennbar.
        </p>
        <p>
          Eine permanente inhaltliche Kontrolle der verlinkten Seiten ist jedoch ohne konkrete Anhaltspunkte einer Rechtsverletzung nicht zumutbar. Bei Bekanntwerden von Rechtsverletzungen werde ich derartige Links umgehend entfernen.
        </p>
        <p>
          Die von R.U.N. analysierten Websites sind Eingaben der Nutzer. Für deren Inhalte und für die Richtigkeit der angezeigten Prüfergebnisse übernehme ich keine Gewähr. Die Analyse ist eine technische Momentaufnahme und ersetzt keine rechtliche oder fachliche Beratung.
        </p>
      </LegalSection>

      <LegalSection title="Urheberrecht">
        <p>
          Die durch den Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechtes bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers. Downloads und Kopien dieser Seite sind nur für den privaten, nicht kommerziellen Gebrauch gestattet.
        </p>
        <p>
          Soweit die Inhalte auf dieser Seite nicht vom Betreiber erstellt wurden, werden die Urheberrechte Dritter beachtet. Insbesondere werden Inhalte Dritter als solche gekennzeichnet. Sollten Sie trotzdem auf eine Urheberrechtsverletzung aufmerksam werden, bitte ich um einen entsprechenden Hinweis. Bei Bekanntwerden von Rechtsverletzungen werde ich derartige Inhalte umgehend entfernen.
        </p>
      </LegalSection>

      <p className="text-xs text-neutral-500">Stand: November 2026</p>
    </LegalLayout>
  );
}
