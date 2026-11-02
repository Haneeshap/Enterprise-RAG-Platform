#!/bin/bash
kafka-topics --create --topic doc-ingest --bootstrap-server kafka:29092 --partitions 3 --replication-factor 1
kafka-topics --create --topic doc-ingest-dlq --bootstrap-server kafka:29092 --partitions 1 --replication-factor 1
echo "Topics created"