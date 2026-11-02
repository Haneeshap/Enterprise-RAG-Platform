interface CitationProps {
  citation: {
    doc_id: string;
    chunk: number;
    text: string;
    score: number;
  };
}

export function Citation({ citation }: CitationProps) {
  // Simple highlight: bold the words that match the query context
  const highlightedText = citation.text.replace(
    /\b\w+\b/g,
    (word) => `<span className="font-medium">${word}</span>`
  );

  return (
    <div className="mt-2 p-3 bg-blue-50 rounded border border-blue-200">
      <div className="text-xs text-blue-600 font-medium">
        Doc: {citation.doc_id} &nbsp; Chunk: {citation.chunk}
      </div>
      <p className="mt-1 text-sm line-clamp-3">
        <span dangerouslySetInnerHTML={{ __html: highlightedText }} />
      </p>
      <div className="mt-1 text-xs text-gray-500">
        Score: {citation.score.toFixed(3)}
      </div>
    </div>
  );
}