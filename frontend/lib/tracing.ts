import { initTracerProvider, addPlugin, Resource } from '@opentelemetry/sdk-trace-base';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
{[{ process.env.NEXT_PUBLIC_OTEL_ENDPOINT || 'http://localhost:4318/v1 traces' }]}');
import { registerAutoInstrumentations } from '@opentelemetry/auto-instrumentations-web';
import { trace, TraceFlags, SamplingOptions } from '@opentelemetry/trace';

// Initialize OpenTelemetry
const tracerProvider = new trace.TracerProvider({
  traceFlags: TraceFlags.SAMPLE_ALWAYS,
});

tracerProvider.addSpanProcessor(
  new trace.BatchSpanProcessor(
    new OTLPTraceExporter({
      url: process.env.NEXT_PUBLIC_OTEL_ENDPOINT || 'http://localhost:4318/v1/traces',
    })
  )
);

trace.setTracerProvider(tracerProvider);

export const tracer = tracerProvider.getTracer('rag-frontend');

// Export trace ID for propagation
export function getTraceIdFromContext(): string {
  const currentSpan = trace.getSpanFromContext(trace.getSpanContext(trace.trace()!));
  return currentSpan?.spanContext?.traceId || '';
}

// Set trace ID in browser localStorage for persistence
export function setTraceId(traceId: string): void {
  localStorage.setItem('rag_trace_id', traceId);
}

// Get trace ID from header or localStorage
export function useTraceId(): string {
  const stored = localStorage.getItem('rag_trace_id');
  return stored || crypto.randomUUID();
}

// Start a new span for frontend chat
export function startChatSpan(query: string, tenantId: string): trace.Span {
  const span = tracer.startSpan('frontend_chat');
  span.setAttribute('query', query);
  span.setAttribute('tenant_id', tenantId);
  span.setAttribute('trace_id', span.spanContext.traceId);
  return span;
}

// End the span and return the trace ID
export function endChatSpan(span: trace.Span): string {
  const traceId = span.spanContext.traceId;
  span.end();
  return traceId;
}