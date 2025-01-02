import pathlib

from neomodel import config
import pika

# rabbitmq connection configuration
rmq_host = '127.0.0.1'
rmq_port = 5672
rmq_user = 'rabbitmq'
rmq_password = 'rabbitmq'

# neo4j connection configuration
neo_host = '127.0.0.1'
neo_port = 7687
neo_user = 'neo4j'
neo_password = 'tXOCq81bn7QfGTMJMrkQqP4J1'
neo_db_name = 'machina'

def db_set_config() -> None:
    """set database configiration for neomodel"""
    config.DATABASE_URL = f"bolt://{neo_user}:{neo_password}@{neo_host}:{neo_port}/{neo_db_name}"

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
