import logging

import py_eureka_client.eureka_client as eureka_client

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends

from service.payment_service import PaymentService
from entities.payment_information import PaymentInformation
from entities.payment_status import PaymentSuccess, PaymentFailure

from configs.config import get_config
from security.jwtbearer import JwtBearer

config = get_config()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global config

    await eureka_client.init_async(
        eureka_server=f"{config['eureka_url']}/eureka/",
        app_name="blazebankpaymentservice",
        instance_port=8000,
        instance_host="localhost"
    )
    yield


app = FastAPI(lifespan=lifespan)
payment = PaymentService()
logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

@app.post("/payment/completePayment")
async def completePayment(payment_info: PaymentInformation, token: str = Depends(JwtBearer())) -> PaymentSuccess | PaymentFailure:
    logger.info(f"Received info: {payment_info}")
    return payment.completePayment(payment_info, token)
