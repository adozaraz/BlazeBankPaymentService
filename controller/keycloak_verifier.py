import logging

from fastapi import Security, Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from keycloak import KeycloakOpenID

from configs.config import get_config
from configs.auth_info import authInfo
from entities.payment_information import PaymentInformation


logger = logging.getLogger('uvicorn.error')

config = get_config()

oauth2_schema = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{config['keycloak_url']}/realms/{authInfo['realm']}/protocol/openid-connect/auth",
    tokenUrl=f"{config['keycloak_url']}/realms/{authInfo['realm']}/protocol/openid-connect/token"
)

keycloak_openid = KeycloakOpenID(
    server_url=f"{config['keycloak_url']}/",
    client_id=authInfo['client_id'],
    realm_name=authInfo['realm'],
    client_secret_key=authInfo['client_secret'],
    verify=True
)


async def get_idp_public_key():
    key = f"""-----BEGIN PUBLIC KEY-----\n{keycloak_openid.public_key()}\n-----END PUBLIC KEY-----"""
    return key


async def get_payload(token: str = Security(oauth2_schema)) -> dict:
    try:
        return keycloak_openid.decode_token(
            token
        )
    except Exception as e:
        logger.error('Error happened at the payload')
        logger.error(f'Token: {token}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),  # "Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_payment_info(payload: dict = Depends(get_payload)) -> PaymentInformation:
    try:
        logger.info(payload)
        return PaymentInformation(
            senderCardNumber = payload['senderCardNumber'],
            senderAccountNumber = payload['senderAccountNumber'],
            amount = payload['amount'],
            currencyCode = payload['currencyCode'],
            receiverCardNumber = payload['receiverCardNumber'],
            receiverAccountNumber = payload['receiverAccountNumber'],
            cvv = payload['cvv']
        )
    except Exception as e:
        logger.error(f'Payload: {payload}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),  # "Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )