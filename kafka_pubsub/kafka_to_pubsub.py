from google.cloud import pubsub_v1
from kafka import KafkaConsumer

from .utils import split_args_into_google_and_kafka


class KafkaToPubsub(object):
    def __init__(self, **kwargs):
        google_args, kafka_args = split_args_into_google_and_kafka(kwargs)

        google_project_id = google_args['project_id']
        google_topic = google_args['topic']

        self._kafka_consumer = KafkaConsumer(**kafka_args)
        self._pubsub_producer = pubsub_v1.PublisherClient()

        pubsub_topic_path = self._pubsub_producer.topic_path(google_project_id, google_topic)
        self._pubsub_topic = self._pubsub_producer.create_topic(pubsub_topic_path)
