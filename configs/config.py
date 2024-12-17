import logging
import os


logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)


def get_config():
    config = {
        'card_service_name': os.environ.get('CARD_SERVICE_NAME', 'blazebankcardservice'),
        'keycloak_url': os.environ.get('KEYCLOAK_URL', 'http://keycloak:8080'),
        'eureka_url': os.environ.get('EUREKA_URI', 'http://eureka:8761/eureka'),
    }

    logger.debug(config)

    return config

def get_kafka_config():
    conf = {
        'kafka_config': {
            'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
        },
        'topics_to_send': os.environ.get('TOPICS_TO_SEND', 'blazebankpayment').split(','),
        'banks': os.environ.get('BANKS', 'BlazeBank').split(',')
    }

    logger.debug(conf)
    logger.debug(os.environ.get('TOPICS_TO_SEND', 'blazebankpayment'))
    logger.debug(os.environ.get('TOPICS_TO_SEND', 'blazebankpayment').split(','))

    return conf