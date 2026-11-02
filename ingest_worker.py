import json
import time
from sqlalchemy import text
from app.db.postgres import get_db
from app.kafka.producer import produce_doc_ingest


def process_message(message):
    doc_id = message["doc_id"]
    text = message["text"]
    metadata = message.get("metadata", {})
    tenant_id = message["tenant_id"]
    trace_id = message.get("trace_id", "")
    
    import tiktoken
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    chunk_size = 500
    overlap = 50
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk_tokens = tokens[i:i + chunk_size]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
    
    embedding = [0.1] * 1536
    
    db = get_db()
    try:
        for i, chunk_text in enumerate(chunks):
            db.execute(
                text(
                    "INSERT INTO docs (id, tenant_id, doc_id, chunk_id, text, embedding, metadata, created_at) "
                    "VALUES (:id, :tenant_id, :doc_id, :chunk_id, :text, :embedding, :metadata, :created_at)"
                ),
                {
                    "id": str(uuid4()),
                    "tenant_id": tenant_id,
                    "doc_id": doc_id,
                    "chunk_id": i,
                    "text": chunk_text,
                    "embedding": embedding,
                    "metadata": metadata,
                    "created_at": time.time(),
                },
            )
        db.commit()
        return {"status": "stored", "doc_id": doc_id, "chunks": len(chunks)}
    except Exception as e:
        from app.kafka.producer import produce_doc_ingest
        produce_doc_ingest(
            doc_id=doc_id,
            text=text,
            metadata=metadata,
            tenant_id=tenant_id,
            trace_id=trace_id,
        )
        return {"status": "failed", "doc_id": doc_id, "error": str(e)}


def ingest_worker():
    from app.db.postgres import get_db
    import os
    
    while True:
        try:
            from kafka import KafkaConsumer
            consumer = KafkaConsumer(
                "doc-ingest",
                bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP", "kafka:29092"),
                auto_offset_reset="earliest",
                enable_commit=True,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            )
            
            for message in consumer:
                result = process_message(message.value)
                print(f"Processed message: {result}")
                consumer.commit()
        except Exception as e:
            print(f"Worker error: {e}")
            time.sleep(5)