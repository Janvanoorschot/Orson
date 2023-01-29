class Default:

    broker_connection_retry = True
    broker_connection_max_retries = 0
    broker_connection_timeout = 120
    broker_heartbeat = 10
    broker_transport_options = {
        'consumer_timeout': False
    }
