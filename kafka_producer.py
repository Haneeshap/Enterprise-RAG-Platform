import json
import os
from kafka import KafkaProducer

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:29092")
PRODUCER = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


def produce_doc_ingest(doc_id: str, text: str, metadata: dict, tenant_id: str, trace_id: str):
    message = {
        "doc_id": doc_id,
        "text": text,
        "metadata": metadata,
        "tenant_id": tenant_id,
        "trace_id": trace_id,
    }
    PRODUCER.send("doc-ingest", message)