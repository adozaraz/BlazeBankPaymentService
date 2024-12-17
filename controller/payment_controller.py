import logging
import os

import py_eureka_client.eureka_client as eureka_client

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends

from entities.other_bank_transaction import OtherBankTransaction
from service.payment_service import PaymentService
from entities.payment_information import PaymentInformation
from entities.payment_status import PaymentInformationStatus

from configs.config import get_config
from security.jwtbearer import JwtBearer


config = get_config()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global config

    await eureka_client.init_async(
        eureka_server=config['eureka_url'],
        app_name=os.environ.get("APP_NAME", "blazebankpaymentservicekafkalistener"),
        instance_port=8000
    )
    yield


app = FastAPI(lifespan=lifespan)
payment = PaymentService()
logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

@app.post("/payment/completePayment")
async def completePayment(payment_info: PaymentInformation, token: str = Depends(JwtBearer())) -> PaymentInformationStatus:
    logger.info(f"Received info: {payment_info}")
    return payment.completePayment(payment_info, token)


@app.post("/payment/completePayment/otherBank")
async def completePaymentWithOtherBank(payment_info: OtherBankTransaction):
    logger.info(f"Received info: {payment_info}")
    return payment.completePaymentFromOtherBank(payment_info)

