import logging

from keycloak import KeycloakOpenID
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from configs.config import get_config
from configs.auth_info import authInfo

class JwtBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JwtBearer, self).__init__(auto_error=auto_error)

        self.global_config = get_config()
        self.keycloak = KeycloakOpenID(
            server_url=f"{self.global_config['keycloak_url']}/",
            client_id=authInfo['client_id'],
            realm_name=authInfo['realm'],
            client_secret_key=authInfo['client_secret'],
            verify=True
        )

        self.logger = logging.getLogger('uvicorn.error')

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JwtBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwt: str) -> bool:
        self.logger.info('Decoding JWT')
        try:
            payload = self.keycloak.decode_token(jwt, validate=False, key=self.get_idp_public_key())
        except Exception as e:
            payload = None
            self.logger.error(e)

        self.logger.info('Validating JWT')
        return not payload is None

    def get_idp_public_key(self):
        key = f"""-----BEGIN PUBLIC KEY-----\n{self.keycloak.public_key()}\n-----END PUBLIC KEY-----"""
        return key