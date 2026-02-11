import Link from "next/link";
import ConnectionBadge from "./ConnectionBadge";

interface Citation {
  summary: string;
  level: string;
  confidence: string | null;
  num_sources: number;
  caveat: string | null;
}

interface CandidateCardProps {
  id: string;
  name: string;
  party: string;
  office: string;
  incumbent: boolean;
  hasConnections: boolean;
  topCitation?: Citation;
}

const partyLabels: Record<string, string> = {
  D: "Democrat",
  R: "Republican",
  L: "Libertarian",
  G: "Green",
  I: "Independent",
};

export default function CandidateCard({
  id,
  name,
  party,
  office,
  incumbent,
  hasConnections,
  topCitation,
}: CandidateCardProps) {
  const partyLabel = partyLabels[party] || party;

  return (
    <Link
      href={`/candidate/${id}`}
      className="block border border-gray-200 rounded-lg p-4 hover:border-gray-400 transition-colors"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold">
            {name}
            {incumbent && (
              <span className="ml-2 text-xs text-gray-500 font-normal">
                (Incumbent)
              </span>
            )}
          </h3>
          <p className="text-sm text-gray-500">
            {partyLabel} &middot; {office}
          </p>
        </div>

        <ConnectionBadge
          level={hasConnections ? topCitation?.level || "Contact" : "None found"}
          confidence={topCitation?.confidence}
        />
      </div>

      {hasConnections && topCitation && (
        <p className="mt-2 text-sm text-gray-600">{topCitation.summary}</p>
      )}

      {!hasConnections && (
        <p className="mt-2 text-sm text-green-700">
          No documented Epstein connections found in available records.
        </p>
      )}

      <p className="mt-2 text-xs text-blue-600">
        View details &rarr;
      </p>
    </Link>
  );
}
