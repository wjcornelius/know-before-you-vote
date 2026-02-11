"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const [zip, setZip] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const cleaned = zip.replace(/\D/g, "").slice(0, 5);

    if (cleaned.length !== 5) {
      setError("Please enter a valid 5-digit zip code.");
      return;
    }

    setError("");
    router.push(`/results/${cleaned}`);
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <h1 className="text-4xl font-bold mb-4">Know Before You Vote</h1>

      <p className="text-lg text-gray-600 max-w-xl mb-8">
        Enter your zip code to see which candidates on your ballot have
        documented connections to the Epstein network. All data comes from
        public records with links to primary source documents.
      </p>

      <form onSubmit={handleSubmit} className="w-full max-w-sm">
        <div className="flex gap-2">
          <input
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={5}
            value={zip}
            onChange={(e) => setZip(e.target.value)}
            placeholder="Enter zip code"
            className="flex-1 px-4 py-3 text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-center"
            aria-label="Zip code"
          />
          <button
            type="submit"
            className="px-6 py-3 text-lg font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Search
          </button>
        </div>
        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      </form>

      <div className="mt-16 max-w-2xl text-left">
        <h2 className="text-xl font-semibold mb-4">What this tool does</h2>
        <ul className="space-y-2 text-gray-600">
          <li>
            <strong>Shows your ballot</strong> &mdash; Federal races for your
            zip code
          </li>
          <li>
            <strong>Shows documented connections</strong> &mdash; Only when
            verified by 2+ independent source databases
          </li>
          <li>
            <strong>Links to primary sources</strong> &mdash; Every claim links
            to the actual document, not a news article
          </li>
          <li>
            <strong>Shows clean records too</strong> &mdash; Candidates with no
            connections are explicitly shown as clean
          </li>
        </ul>

        <h2 className="text-xl font-semibold mt-8 mb-4">
          What this tool never does
        </h2>
        <ul className="space-y-2 text-gray-600">
          <li>Accuse anyone of a crime</li>
          <li>Editorialize or express opinions</li>
          <li>Recommend how to vote</li>
          <li>Treat different parties differently</li>
        </ul>
      </div>
    </div>
  );
}
