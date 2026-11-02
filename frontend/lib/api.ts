import { open } from 'stream';

// Mock API base URL - in production this would be your backend URL
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function streamChat(
  query: string,
  tenantId: string,
  traceId: string
): Promise<AsyncGenerator<any, void, any>> {
  const response = await fetch(`${API_BASE}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Trace-ID': traceId,
      'X-Correlation-ID': crypto.randomUUID(),
    },
    body: JSON.stringify({ query, tenant_id: tenantId }),
  });

  if (!response.ok) {
    throw new Error(`Streaming failed: ${response.statusText}`);
  }

  // Handle SSE (Server-Sent Events)
  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body');

  const decoder = new TextDecoderStream();
  reader.pipeThrough(decoder);

  let buffer = '';
  let inEvent = false;
  let currentEvent = '';

  return new AsyncGenerator(async function* () {
    for await (const chunk of reader) {
      buffer += chunk;

      while (buffer.includes('\n')) {
        const [line, ...rest] = buffer.split('\n');
        buffer = rest.join('\n');

        if (line.startsWith('event:')) {
          inEvent = line.substring('event:'.length).trim() === 'token';
        } else if (line.startsWith('data:')) {
          const data = line.substring('data:'.length).trim();
          if (!data) continue;

          try {
            const parsed = JSON.parse(data);
            
            if (inEvent && parsed.type === 'token') {
              // Yield token event
              yield { type: 'token', data: { token: parsed.content } };
            } else if (!inEvent && parsed.type === 'citation') {
              // Yield citation event
              yield { type: 'citation', data: parsed };
            } else if (parsed.type === 'done') {
              // Yield done event
              yield { type: 'done', data: parsed };
              return; // Generator completes
            }
          } catch (e) {
            console.error('JSON parse error:', e, 'data:', data);
          }
        }
      }
    }
  });
}