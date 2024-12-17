import logging
import json

import requests
import py_eureka_client.eureka_client as eureka_client

from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient

from configs.auth_info import authInfo
from configs.config import get_config, get_kafka_config


conf = get_config()
kafka_config = get_kafka_config()
logger = logging.getLogger('uvicorn.error')

producer = Producer(kafka_config.get('kafka_config'))

def authenticate_in_keycloak():

    body = {
        'username': 'paymentservicemasteraccount',
        'password': 'paymentservice',
        'grant_type': 'password',
        'client_id': authInfo.get('client_id')
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    url = f"{conf.get('keycloak_url')}/realms/{authInfo.get('realm')}/protocol/openid-connect/token"
    response = requests.post(url, headers=headers, data=body)
    response = response.json()

    return response.get('access_token')


def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))
    logger.info(msg)


def send_message(topic, message: dict):
    kadmin = AdminClient(kafka_config.get('kafka_config'))

    logger.debug(kadmin.list_topics().topics)
    logger.debug(topic)
    logger.debug(message)

    producer.poll(0)
    producer.produce(topic, value=json.dumps(message).encode('utf-8'), callback=delivery_report)
    producer.flush()


def get_bank_topic(bank: str) -> str:
    logger.debug(f'Kafka config: {kafka_config}')
    bank_to_topic_map = dict(zip(kafka_config.get('banks'), kafka_config.get('topics_to_send')))
    return bank_to_topic_map.get(bank, 'blazebankpayment')


def get_service_instance(service_name):
    app = eureka_client.get_client().applications.get_application(service_name)
    active_instance = app.up_instances[0]

    return f'http://{active_instance.ipAddr}:{active_instance.port.port}'