import pathlib

import pika

# connection configuration
rmq_host = '127.0.0.1'
rmq_port = 5672
rmq_user = 'rabbitmq'
rmq_password = 'rabbitmq'

_test_dir = pathlib.Path(__file__).resolve().parent
test_data_dir = pathlib.Path(_test_dir, 'data').resolve()

def get_rmq_conn() -> pika.BlockingConnection:
    """get a new rabbitmq `pika.BlockingConnection` object

    :return: the new connection object
    """
    credentials = pika.PlainCredentials(
        rmq_user,
        rmq_password)

    parameters = pika.ConnectionParameters(
        rmq_host,
        rmq_port,
        '/',
        credentials,
        socket_timeout=2)
    
    connection = pika.BlockingConnection(parameters)

    return connection
