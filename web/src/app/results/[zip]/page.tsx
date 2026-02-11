import Link from "next/link";
import CandidateCard from "@/components/CandidateCard";

// Sample data - will be replaced by actual JSON from pipeline
const SAMPLE_CANDIDATES = [
  {
    id: "ca-senate-example-senator",
    name: "Example Senator",
    party: "D",
    office: "U.S. Senate",
    incumbent: true,
  },
  {
    id: "ca-22-example-representative",
    name: "Example Representative",
    party: "R",
    office: "U.S. House",
    incumbent: true,
  },
];

interface ResultsPageProps {
  params: Promise<{ zip: string }>;
}

export default async function ResultsPage({ params }: ResultsPageProps) {
  const { zip } = await params;

  // TODO: Load from districts.json, candidates.json, connections.json
  // For now, show placeholder
  const isDataAvailable = false;

  return (
    <div>
      <div className="mb-8">
        <Link href="/" className="text-sm text-blue-600 hover:underline">
          &larr; New search
        </Link>
        <h1 className="text-3xl font-bold mt-2">
          Results for {zip}
        </h1>
        <p className="text-gray-500 mt-1">
          Federal races on your ballot
        </p>
      </div>

      {!isDataAvailable && (
        <div className="border border-yellow-200 bg-yellow-50 rounded-lg p-6 text-center">
          <h2 className="text-xl font-semibold text-yellow-800 mb-2">
            Data Pipeline Not Yet Active
          </h2>
          <p className="text-yellow-700">
            The automated data pipeline has not yet run. Once active, this page
            will show candidates for zip code {zip} with their documented
            Epstein connections (or lack thereof).
          </p>
          <p className="text-yellow-600 text-sm mt-4">
            The pipeline downloads entity data from 4 independent Epstein
            analysis projects, cross-references against current candidates via
            the FEC and ProPublica APIs, and requires 2+ source databases to
            agree before displaying any connection.
          </p>
        </div>
      )}

      {isDataAvailable && (
        <>
          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4">U.S. Senate</h2>
            <div className="space-y-3">
              {SAMPLE_CANDIDATES.filter((c) => c.office === "U.S. Senate").map(
                (c) => (
                  <CandidateCard
                    key={c.id}
                    {...c}
                    hasConnections={false}
                  />
                )
              )}
            </div>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-4">U.S. House</h2>
            <div className="space-y-3">
              {SAMPLE_CANDIDATES.filter((c) => c.office === "U.S. House").map(
                (c) => (
                  <CandidateCard
                    key={c.id}
                    {...c}
                    hasConnections={false}
                  />
                )
              )}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
