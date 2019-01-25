def split_args_into_google_and_kafka(args):
    """
    Split a dict of arguments into Google and Kafka dictionaries, based on the key prefixes.

    >>> from pprint import pprint
    >>> pprint(split_args_into_google_and_kafka({'kafka_bootstrap_servers': 'localhost', 'google_topic': 'foo',
    ...     'kafka_group_id': 'mygroup', 'google_project_id': 'myproject'}))
    ({'project_id': 'myproject', 'topic': 'foo'},
     {'bootstrap_servers': 'localhost', 'group_id': 'mygroup'})
    """
    google_args = {k[7:]: v for k, v in args.items() if k.startswith('google_')}
    kafka_args = {k[6:]: v for k, v in args.items() if k.startswith('kafka_')}

    return google_args, kafka_args


def init_common_args_parser():
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-b', '--bootstrap-servers', help='Kafka bootstrap servers',
                        required=True, default='localhost')
    parser.add_argument('-p', '--project-id', help='Google Cloud project ID', required=True)
    parser.add_argument('--kafka-topic', help='Kafka topic', required=True)
    parser.add_argument('--pubsub-topic', help='Google PubSub topic', required=True)
    parser.add_argument('--loglevel', help='Logging level',
                        choices=('debug', 'info', 'warn', 'error'), default='info')

    return parser


def config_logging(level):
    import logging

    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % level)
    logging.basicConfig(format='[%(asctime)s][%(levelname)s/%(threadName)s] %(message)s',
                        level=numeric_level)
