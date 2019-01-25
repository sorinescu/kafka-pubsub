import logging

from google.api_core import exceptions as google_exceptions
from google.cloud import pubsub_v1
from kafka import KafkaConsumer

from .utils import split_args_into_google_and_kafka

_logger = None


def _get_logger():
    global _logger

    if _logger is None:
        _logger = logging.getLogger(__name__)
    return _logger


class KafkaToPubSub(object):
    def __init__(self, message_transformer=None, **kwargs):
        self._message_transformer = message_transformer

        google_args, kafka_args = split_args_into_google_and_kafka(kwargs)

        google_project_id = google_args.pop('project_id')
        google_topic = google_args.pop('topic')
        kafka_topic = kafka_args.pop('topic')

        self._kafka_consumer = KafkaConsumer(**kafka_args)
        self._kafka_consumer.subscribe([kafka_topic])

        self._pubsub_producer = pubsub_v1.PublisherClient(**google_args)

        self._pubsub_topic_path = self._pubsub_producer.topic_path(google_project_id, google_topic)

        try:
            self._pubsub_topic = self._pubsub_producer.get_topic(self._pubsub_topic_path)
        except google_exceptions.NotFound:
            self._pubsub_topic = self._pubsub_producer.create_topic(self._pubsub_topic_path)

        _get_logger().info("Consuming from Kafka '%s' on '%s' and producing to PubSub '%s' on '%s'" %
                           (kafka_args['bootstrap_servers'], kafka_topic,
                            self._pubsub_topic_path, google_project_id))

    def run_proxy(self, max_records=None, timeout_ms=5000, metadata=None):
        if metadata is None:
            metadata = {}

        messages = self._kafka_consumer.poll(timeout_ms=timeout_ms, max_records=max_records)
        _get_logger().debug('Got %d Kafka messages' % sum([len(msg_list) for msg_list in messages.values()]))

        for msg_list in messages.values():
            for msg in msg_list:
                if self._message_transformer is not None:
                    value = self._message_transformer(msg)
                else:
                    value = msg.value

                _get_logger().debug("Publishing to PubSub %r with metadata %r" % (value, metadata))
                self._pubsub_producer.publish(self._pubsub_topic_path, value, **metadata)

    def run_forever(self, max_records=None, metadata=None):
        while True:
            self.run_proxy(max_records=max_records, metadata=metadata)


def main():
    import socket
    from .utils import config_logging, init_common_args_parser

    parser = init_common_args_parser()
    parser.add_argument('-g', '--group-id', help='Kafka consumer group ID', required=True)

    args = parser.parse_args()

    config_logging(args.loglevel)

    consumer_name = "kafka-to-pubsub-%s" % socket.gethostname()

    k2p = KafkaToPubSub(kafka_bootstrap_servers=args.bootstrap_servers,
                        kafka_client_id=consumer_name,
                        kafka_group_id=args.group_id,
                        kafka_topic=args.kafka_topic,
                        google_project_id=args.project_id,
                        google_topic=args.pubsub_topic)

    k2p.run_forever()
