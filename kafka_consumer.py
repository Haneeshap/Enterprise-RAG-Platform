from kafka import KafkaConsumer

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:29092")
CONSUMER = KafkaConsumer(
    "doc-ingest",
    bootstrap_servers=KAFKA_BOOTSTRAP,
    auto_offset_reset="earliest",
    enable_commit=True,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
)


def consume_messages():
    for message in CONSUMER:
        yield message.value