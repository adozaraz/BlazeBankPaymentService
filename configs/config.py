import os

def get_config():
    config = {
        'card_service_url': os.environ.get('CARD_SERVICE_URL', 'http://card-service:8111'),
        'keycloak_url': os.environ.get('KEYCLOAK_URL', 'http://keycloak:8080'),
        'eureka_url': os.environ.get('EUREKA_URL', 'http://eureka:8761'),
    }

    return config