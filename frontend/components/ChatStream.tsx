import { useState, useEffect, useRef } from 'react';
import Citation from './Citation';

export function ChatStream({ initialQuery }: { initialQuery?: string }) {
  const [query, setQuery] = useState(initialQuery || '');
  const [messages, setMessages] = useState<
    Array<{ role: 'user' | 'assistant'; content: string; citations?: any[]; ttfb?: number }>
  >([]);
  const [ttfb, setTtfb] = useState(0);
  const [traceId, setTraceId] = useState<string>('');
  const [cached, setCached] = useState(false);
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    if (!traceId) {
      const uuid = self.crypto?.randomUUID?.() || Math.random().toString(36).substr(2, 24);
      setTraceId(uuid);
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setMessages((prev) => [...prev, { role: 'user', content: query }]);
    setQuery('');

    const eventSource = new EventSource(`/chat/stream?query=${encodeURIComponent(query)}&tenant_id=test1`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.event === 'token') {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          const content = last?.role === 'assistant'
            ? last.content + data.token
            : data.token;
          return [
            ...prev.slice(0, -1),
            { ...last, role: 'assistant', content },
          ];
        });
      }

      if (data.event === 'citation') {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          return [
            ...prev.slice(0, -1),
            {
              ...last,
              citations: [
                ...(last?.citations || []),
                {
                  doc_id: data.citation.doc_id,
                  chunk: data.citation.chunk,
                  text: data.citation.text,
                  score: data.citation.score,
                  highlight: data.citation.highlight,
                },
              ],
            },
          ];
        });
      }

      if (data.event === 'done') {
        setCached(data.cached || false);
        setTtfb(data.ttfb_ms || 0);
        setTraceId(data.trace_id || '');
        eventSource.close();
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        return [
          ...prev.slice(0, -1),
          { role: 'assistant', content: 'Connection error', ttfb: 0 },
        ];
      });
    };
  };

  if (messages.length === 0) {
    return <div>Start a conversation above.</div>;
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="mb-6 text-xl font-bold">Enterprise RAG Chat Stream</h2>

      <div className="space-y-4">
        <div className="h-96 overflow-y-auto border rounded-lg p-4">
          {messages.map((msg, idx) => (
            <div key={idx} className={
              msg.role === 'user'
                ? 'bg-blue-100 rounded-md p-3 text-right'
                : 'bg-gray-100 rounded-md p-3'
            }>
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.citations?.length > 0 && (
                <div className="mt-2">
                  {msg.citations.map((citation, i) => (
                    <Citation key={i} citation={citation} />
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="flex items-center justify-between pt-4 pt-0 border-t">
          <div className="flex items-center">
            <span className="text-sm text-gray-600">
              TTFB: {ttfb > 0 ? `${ttfb} ms` : '—'}
            </span>
          </div>
          <div className="flex items-center">
            <span className="text-sm text-gray-600">
              Cached: {cached ? 'Yes' : 'No'}
            </span>
          </div>
        </div>

        <form
          ref={formRef}
          onSubmit={handleSubmit}
          className="mt-6 flex items-end gap-2"
        >
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question..."
            className="flex-1 rounded-l-lg py-3 px-4 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
            disabled={true}
          />
          <button
            type="submit"
            disabled={true}
            className="rounded-r-lg py-3 px-4 border border-gray-300 bg-primary-600 text-white font-medium hover:bg-primary-700 disabled:opacity-50"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}