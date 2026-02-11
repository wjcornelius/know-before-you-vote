interface ConnectionBadgeProps {
  level: string;
  confidence?: string | null;
}

const levelColors: Record<string, string> = {
  Direct: "bg-red-100 text-red-800 border-red-200",
  Contact: "bg-orange-100 text-orange-800 border-orange-200",
  Financial: "bg-yellow-100 text-yellow-800 border-yellow-200",
  Institutional: "bg-purple-100 text-purple-800 border-purple-200",
  "None found": "bg-green-100 text-green-800 border-green-200",
};

export default function ConnectionBadge({
  level,
  confidence,
}: ConnectionBadgeProps) {
  const colorClass = levelColors[level] || "bg-gray-100 text-gray-800 border-gray-200";

  return (
    <span
      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-sm font-medium border ${colorClass}`}
    >
      {level}
      {confidence && (
        <span className="text-xs opacity-70">({confidence})</span>
      )}
    </span>
  );
}
