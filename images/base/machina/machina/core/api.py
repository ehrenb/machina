import logging
import pika
import time

logger = logging.getLogger(__name__)


class BaseAPI(object):
    def __init__(self, 
                 rabbitmq_host,
                 rabbitmq_port,
                 rabbitmq_user,
                 rabbitmq_password,
                 rabbitmq_heartbeat):
        self.connection = None
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
        parameters = pika.ConnectionParameters(rabbitmq_host,
                                               int(rabbitmq_port),
                                               '/',
                                               credentials,
                                               heartbeat=int(rabbitmq_heartbeat),
                                               socket_timeout=2)
        max_retries = 5
        attempt = 0
        while attempt < max_retries:
            try:
                logger.info("Attempt {}/{} to connect to RabbitMQ at {}:{}".format(attempt, max_retries, rabbitmq_host, rabbitmq_port))
                self.connection = pika.BlockingConnection(parameters)
                break
            except pika.exceptions.AMQPConnectionError as e:
                logger.exception("Error connecting to RabbitMQ")
                time.sleep(0.5)
                attempt += 1