"""
scraper/kafka_producer.py
Kafka producer interface with in-memory fallback for local standalone execution.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

class APIxKafkaProducer:
    """Publishes raw fare quotes to Kafka raw_fares topic or in-memory fallback."""
    def __init__(self, bootstrap_servers: Optional[str] = None):
        self.bootstrap = bootstrap_servers or os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")
        self.topic = os.environ.get("KAFKA_TOPIC_RAW", "raw_fares")
        self._producer = None
        self._memory_buffer: List[Dict[str, Any]] = []
        self._init_producer()

    def _init_producer(self):
        try:
            from kafka import KafkaProducer
            self._producer = KafkaProducer(
                bootstrap_servers=self.bootstrap,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",
                retries=3,
                request_timeout_ms=5000
            )
            logger.info(f"Connected to Kafka broker at {self.bootstrap}")
        except Exception as e:
            logger.warning(f"Kafka connection not active ({e}). Using in-memory message queue fallback.")
            self._producer = None

    def send(self, topic: Optional[str], key: Optional[str] = None, value: Optional[Any] = None):
        target_topic = topic or self.topic
        payload = value
        if isinstance(value, bytes):
            try:
                payload = json.loads(value.decode("utf-8"))
            except Exception:
                pass
        
        if self._producer:
            try:
                k_bytes = key.encode("utf-8") if isinstance(key, str) else key
                v_bytes = json.dumps(payload).encode("utf-8") if not isinstance(payload, bytes) else payload
                self._producer.send(target_topic, key=k_bytes, value=v_bytes)
                return
            except Exception as e:
                logger.error(f"Kafka send failed: {e}. Falling back to memory buffer.")

        # Fallback
        self._memory_buffer.append(payload if isinstance(payload, dict) else {"data": payload})

    def flush(self):
        if self._producer:
            try:
                self._producer.flush()
            except Exception as e:
                logger.error(f"Error flushing Kafka: {e}")

    def close(self):
        if self._producer:
            try:
                self._producer.close()
            except Exception:
                pass

    def get_buffered_records(self) -> List[Dict[str, Any]]:
        records = list(self._memory_buffer)
        self._memory_buffer.clear()
        return records
