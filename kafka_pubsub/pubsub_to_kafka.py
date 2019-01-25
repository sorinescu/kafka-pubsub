import logging

from google.api_core import exceptions as google_exceptions
from google.cloud import pubsub_v1
from kafka import KafkaProducer

from .utils import split_args_into_google_and_kafka

_logger = None


def _get_logger():
    global _logger

    if _logger is None:
        _logger = logging.getLogger(__name__)
    return _logger


class PubSubToKafka(object):
    def __init__(self, message_transformer=None, **kwargs):
        self._message_transformer = message_transformer

        google_args, kafka_args = split_args_into_google_and_kafka(kwargs)

        google_project_id = google_args.pop('project_id')
        google_topic = google_args.pop('topic')
        google_subscription_name = google_args.pop('subscription_name')

        self._kafka_topic = kafka_args.pop('topic')
        self._kafka_producer = KafkaProducer(**kafka_args)

        self._pubsub_consumer = pubsub_v1.SubscriberClient(**google_args)

        self._pubsub_topic_path = self._pubsub_consumer.topic_path(google_project_id, google_topic)
        self._pubsub_subscription_path = self._pubsub_consumer.subscription_path(google_project_id,
                                                                                 google_subscription_name)

        try:
            self._pubsub_consumer.create_subscription(self._pubsub_subscription_path,
                                                      self._pubsub_topic_path)
        except google_exceptions.AlreadyExists:
            pass

        self._pubsub_future = self._pubsub_consumer.subscribe(self._pubsub_subscription_path,
                                                              self._on_pubsub_message)

        _get_logger().info("Consuming from PubSub '%s' on '%s' and producing to Kafka '%s' on '%s'" %
                           (self._pubsub_subscription_path, google_project_id,
                            self._kafka_topic, kafka_args['bootstrap_servers']))

    def _on_pubsub_message(self, message):
        _get_logger().debug("Got PubSub message %r" % message)
        
        if self._message_transformer is not None:
            value = self._message_transformer(message)
        else:
            value = message.data

        self._kafka_producer.send(self._kafka_topic, value)
        message.ack()

    def run_proxy(self, timeout_ms=5000):
        try:
            ex = self._pubsub_future.exception(timeout_ms / 1000.0)
            if ex is not None:
                raise ex
        except pubsub_v1.exceptions.TimeoutError:
            pass

    def run_forever(self):
        while True:
            self.run_proxy()


def main():
    from .utils import config_logging, init_common_args_parser

    parser = init_common_args_parser()
    parser.add_argument('-s', '--subscription', help='Google PubSub subscription name',
                        required=True)

    args = parser.parse_args()

    config_logging(args.loglevel)

    p2k = PubSubToKafka(kafka_bootstrap_servers=args.bootstrap_servers,
                        kafka_topic=args.kafka_topic,
                        google_project_id=args.project_id,
                        google_topic=args.pubsub_topic,
                        google_subscription_name=args.subscription)

    p2k.run_forever()
