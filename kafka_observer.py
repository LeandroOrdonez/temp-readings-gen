from kafka import KafkaProducer
from requests.auth import HTTPBasicAuth
import json
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

class KafkaObserver():
    """
    (c) Tengu.io
    Sends records to their appropriate topic.
    Attributes:
        kafka_brokers: List of full Kafka broker addresses.
        topic: The kafka topic the message should be send to.
    """
    def __init__(self, kafka_brokers, topic):
        self.kafka_brokers = kafka_brokers
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=kafka_brokers,
            value_serializer=lambda m: json.dumps(m).encode('utf-8'))
        self.topic = topic

    def on_next(self, message):
        logger.debug("Sending data to topic {}...".format(self.topic))
        self.kafka_producer.send(topic=self.topic, value=message)
        logger.debug("Success!")

    def on_completed(self):
        logger.info("KafkaObserver completed!")

    def on_error(self, error):
        logger.error("Error occurred in KafkaObserver: {}".format(error))
        os._exit(1)