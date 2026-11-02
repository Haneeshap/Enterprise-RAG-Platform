import { useState, useEffect, useRef } from 'react';
import Citation from './Citation';
import { streamChat } from '@/lib/api';

interface ChatProps {
  initialQuery?: string;
  initialTenantId?: string;
}

export function Chat({ initialQuery }: ChatProps = {}) {
  const [query, setQuery] = useState(initialQuery || '');
  const [messages, setMessages] = useState<
    Array<{ role: 'user' | 'assistant'; content: string; citations?: any[]; ttfb?: number; cost?: number }>
  >([]);
  const [isLoading, setIsLoading] = useState(false);
  const [ttfb, setTtfb] = useState(0);
  const [traceId, setTraceId] = useState<string>('');
  const [cost, setCost] = useState(0);
  const [cacheHit, setCacheHit] = useState(false);
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    // Generate a new trace ID if not present
    if (!traceId) {
      const uuid = self.crypto?.randomUUID?.() || Math.random().toString(36).substr(2, 24);
      setTraceId(uuid);
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    setIsLoading(true);
    setMessages((prev) => [...prev, { role: 'user', content: query, ttfb: 0, cost: 0 }]);
    setQuery('');

    const startTime = performance.now();
    let firstTokenTime: number | null = null;

    const events: any[] = [];

    try {
      const response = await streamChat(query, initialTenantId || 'tenant1', traceId);

      for await (const event of response) {
        if (event.type === 'token') {
          if (!firstTokenTime) {
            firstTokenTime = performance.now();
            setTtfb(Math.round(firstTokenTime - startTime));
          }
          setMessages((prev) => {
            const last = prev[prev.length - 1];
            const content =
              last?.role === 'assistant'
                ? last.content + event.data.token
                : event.data.token;
            return [
              ...prev.slice(0, -1),
              { ...last, role: 'assistant', content, citations: last?.citations },
            ];
          });
        }

        if (event.type === 'citation') {
          setMessages((prev) => {
            const last = prev[prev.length - 1];
            return [
              ...prev.slice(0, -1),
              {
                ...last,
                citations: [
                  ...(last?.citations || []),
                  {
                    doc_id: event.data.doc_id,
                    chunk: event.data.chunk,
                    text: event.data.text,
                    score: event.data.score,
                  },
                ],
              },
            ];
          });
        }

        if (event.type === 'done') {
          setIsLoading(false);
          setCost(event.data.cost);
          setCacheHit(event.data.cache_hit || false);
          setTraceId(event.data.trace_id);
        }
      }
    } catch (error) {
      console.error('Streaming error:', error);
      setIsLoading(false);
    }
  };

  if (isLoading && messages.length === 0) {
    return <div>Loading initial message...</div>;
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="mb-6 text-xl font-bold">Enterprise RAG Chat</h2>

      <div className="space-y-4">
        {/* Chat messages */}
        <div className="h-96 overflow-y-auto border rounded-lg p-4">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={
                msg.role === 'user'
                  ? 'bg-blue-100 rounded-md p-3 text-right'
                  : 'bg-gray-100 rounded-md p-3'
              }
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.citations?.length > 0 && (
                <div className="mt-2 text-sm">
                  {msg.citations.map((citation, i) => (
                    <Citation key={i} citation={citation} />
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* TTFB and Cost display */}
        <div className="flex items-center justify-between pt-4 pt-0 border-t">
          <div className="flex items-center">
            <span className="text-sm text-gray-600">
              TTFB: {ttfb > 0 ? `${ttfb} ms` : '—'} &
              Cost: ${cost > 0 ? `$${cost.toFixed(4)}` : '—'}
            </span>
          </div>
          <div className="flex items-center">
            <span className="text-sm text-gray-600">
              Cache: {cacheHit ? 'Hit' : 'Miss'}
            </span>
          </div>
        </div>

        {/* Chat form */}
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
            className="flex-1 rounded-l-lg py-3 px-4 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading}
            className="rounded-r-lg py-3 px-4 border border-gray-300 bg-primary-600 text-white font-medium hover:bg-primary-700 disabled:opacity-50"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}