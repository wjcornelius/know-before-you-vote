export default function MethodologyPage() {
  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">How This Works</h1>

      <section className="mb-10">
        <h2 className="text-xl font-semibold mb-3">Data Sources</h2>
        <p className="text-gray-600 mb-4">
          All data comes from publicly available records. No private databases,
          no anonymous tips, no unverified claims.
        </p>
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2 pr-4">Source</th>
              <th className="text-left py-2">What It Contains</th>
            </tr>
          </thead>
          <tbody className="text-gray-600">
            <tr className="border-b">
              <td className="py-2 pr-4 font-medium">DOJ Epstein Library</td>
              <td className="py-2">
                3.5 million pages released January 30, 2026
              </td>
            </tr>
            <tr className="border-b">
              <td className="py-2 pr-4 font-medium">Epstein Doc Explorer</td>
              <td className="py-2">
                15,000+ relationships extracted from email corpus
              </td>
            </tr>
            <tr className="border-b">
              <td className="py-2 pr-4 font-medium">LMSBAND Files DB</td>
              <td className="py-2">
                Named entities from DOJ Datasets 8-12
              </td>
            </tr>
            <tr className="border-b">
              <td className="py-2 pr-4 font-medium">SvetimFM Analysis</td>
              <td className="py-2">
                68,798 documents with entity networks
              </td>
            </tr>
            <tr className="border-b">
              <td className="py-2 pr-4 font-medium">phelix001 Network</td>
              <td className="py-2">
                19,154 FOIA documents with categorized entities
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <section className="mb-10">
        <h2 className="text-xl font-semibold mb-3">
          Multi-Source Corroboration
        </h2>
        <p className="text-gray-600 mb-4">
          A connection is only displayed when it appears in{" "}
          <strong>2 or more independent source databases</strong>. This is the
          primary quality control mechanism.
        </p>
        <ul className="space-y-2 text-gray-600">
          <li>
            <strong>3+ sources</strong> = HIGH confidence &mdash; displayed with
            full confidence
          </li>
          <li>
            <strong>2 sources</strong> = MEDIUM confidence &mdash; displayed
            with a &ldquo;limited documentation&rdquo; note
          </li>
          <li>
            <strong>1 source</strong> = NOT displayed &mdash; too high a risk of
            database noise or name collision
          </li>
          <li>
            <strong>0 sources</strong> = &ldquo;No documented connections
            found&rdquo;
          </li>
        </ul>
      </section>

      <section className="mb-10">
        <h2 className="text-xl font-semibold mb-3">Connection Levels</h2>
        <p className="text-gray-600 mb-4">
          Not all connections are equal. The tool clearly distinguishes between
          levels based on what documents actually show:
        </p>
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2 pr-4">Level</th>
              <th className="text-left py-2">What It Means</th>
            </tr>
          </thead>
          <tbody className="text-gray-600">
            <tr className="border-b">
              <td className="py-2 pr-4 font-medium text-red-700">Direct</td>
              <td className="py-2">
                Named as participant in activities: victim testimony, evidence of
                criminal conduct
              </td>
            </tr>
            <tr className="border-b">
              <td className="py-2 pr-4 font-medium text-orange-700">
                Contact
              </td>
              <td className="py-2">
                Documented communication or social contact: flight logs, emails,
                event attendance
              </td>
            </tr>
            <tr className="border-b">
              <td className="py-2 pr-4 font-medium text-yellow-700">
                Financial
              </td>
              <td className="py-2">
                Campaign donations from Epstein or documented associates
              </td>
            </tr>
            <tr className="border-b">
              <td className="py-2 pr-4 font-medium text-purple-700">
                Institutional
              </td>
              <td className="py-2">
                Held position with authority over Epstein investigations
              </td>
            </tr>
            <tr className="border-b">
              <td className="py-2 pr-4 font-medium text-green-700">
                None found
              </td>
              <td className="py-2">
                No documented connection in available records
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <section className="mb-10">
        <h2 className="text-xl font-semibold mb-3">Name Matching</h2>
        <p className="text-gray-600 mb-4">
          Matching names between Epstein documents and current candidates uses a
          two-phase process to prevent false matches:
        </p>
        <ol className="list-decimal list-inside space-y-2 text-gray-600">
          <li>
            <strong>Fuzzy string matching</strong> with a high threshold (92%)
            catches spelling variations, nicknames, and title differences
          </li>
          <li>
            <strong>AI disambiguation</strong> uses biographical context (state,
            office, career) to confirm the candidate and the document entity are
            actually the same person. &ldquo;John Kennedy&rdquo; from Louisiana
            is not &ldquo;John F. Kennedy&rdquo; from the 1960s.
          </li>
        </ol>
      </section>

      <section className="mb-10">
        <h2 className="text-xl font-semibold mb-3">Updates</h2>
        <p className="text-gray-600">
          The data pipeline runs automatically. Candidate lists update as
          primaries conclude and new filings are made with the FEC. Epstein
          document analysis updates as the community projects publish new
          extractions. News monitoring checks daily for newly revealed
          connections.
        </p>
      </section>

      <section className="mb-10">
        <h2 className="text-xl font-semibold mb-3">Corrections</h2>
        <p className="text-gray-600">
          If you find an error, please report it via{" "}
          <a
            href="https://github.com/wjcornelius/know-before-you-vote/issues"
            className="text-blue-600 underline"
          >
            GitHub Issues
          </a>
          . Corrections are made immediately and documented publicly.
        </p>
      </section>

      <section className="border-t pt-6">
        <h2 className="text-xl font-semibold mb-3">Legal</h2>
        <p className="text-gray-600 text-sm">
          This tool presents publicly available records. It does not accuse
          anyone of criminal conduct. Connection levels describe the nature of
          documented contact, not guilt or innocence. All data comes from
          government-published documents, court filings, and legally required
          campaign finance disclosures. Publishing factual information about
          public officials is protected by the First Amendment.
        </p>
      </section>
    </div>
  );
}
