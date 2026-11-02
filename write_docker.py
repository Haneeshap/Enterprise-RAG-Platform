import sys

content = """version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+psycopg2://rag:rag@postgres:5432/rag
      - REDIS_HOST=redis
      - JWT_SECRET=your-jwt-secret-key
      - CORS_ORIGINS=http://localhost:3000
      - JAEGER_AGENT_HOST=jaeger
      - JAEGER_AGENT_PORT=14268
      - OTEL_EXPORTER_JAEGER_ENDPOINT=http://jaeger:14268/api/traces
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: rag
      POSTGRES_USER: rag
      POSTGRES_PASSWORD: rag
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthchecks:
      test: ["CMD-SHELL", "pg_isready -U rag"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthchecks:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  kafka:
    image: confluentinc/cp-kafka:7.4.0
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    healthchecks:
      test: ["CMD", "kafka-topics", "--list", "--bootstrap-server", "localhost:9092"]
      interval: 10s
      timeout: 5s
      retries: 5

  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    ports:
      - "2181:2181"
    healthchecks:
      test: ["CMD", "echo", "stat | grep -e 'latch' -e 'sync' | grep 'Mode:'"]
      interval: 10s
      timeout: 5s
      retries: 5

  loki:
    image: grafana/loki:2.9.0
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - ./loki-config.yaml:/etc/loki/local-config.yaml
    healthchecks:
      test: ["CMD", "curl", "-f", "http://localhost:3100/ready"]
      interval: 15s
      timeout: 10s
      retries: 6

  promtail:
    image: grafana/promtail:2.9.0
    volumes:
      - ./promtail-config.yml:/etc/promtail/config.yml
      - ./:/var/log/app:ro
    command: -config.file=/etc/promtail/config.yml
    depends_on:
      - loki

  jaeger:
    image: jaegertracing/all-in-one:1.51
    ports:
      - "16686:16686"
      - "14268:14268"
    healthchecks:
      test: ["CMD", "curl", "-f", "http://localhost:14268/api/traces"]
      interval: 15s
      timeout: 10s
      retries: 6

  grafana:
    image: grafana/grafana:10.2.0
    ports:
      - "3000:3000"
    depends_on:
      - loki
      - jaeger
    environment:
      - PANADA_ENABLED=true

volumes:
  postgres_data:
  redis_data:
  loki-data:
"""

with open("c:\\Users\\hanee\\Enterprise RAG Platform\\docker-compose.yml", "w") as f:
    f.write(content)

print("Docker compose written successfully")
"""

import subprocess
result = subprocess.run(["python", "write_docker.py"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)