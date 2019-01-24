def split_args_into_google_and_kafka(args):
    """
    Split a dict of arguments into Google and Kafka dictionaries, based on the key prefixes.

    >>> split_args_into_google_and_kafka({'kafka_bootstrap_servers': 'localhost', 'google_topic': 'foo',
    ...     'kafka_group_id': 'mygroup', 'google_project_id': 'myproject'})
    ({'topic': 'foo', 'project_id': 'myproject'}, {'bootstrap_servers': 'localhost', 'group_id': 'mygroup'})
    """
    google_args = {k[7:]: v for k, v in args.items() if k.startswith('google_')}
    kafka_args = {k[6:]: v for k, v in args.items() if k.startswith('kafka_')}

    return google_args, kafka_args
