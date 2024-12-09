import py_eureka_client.eureka_client as eureka_client

from contextlib import asynccontextmanager

from fastapi import FastAPI

from service.payment_service import PaymentService
from entities.payment_information import PaymentInformation
from entities.payment_status import PaymentSuccess, PaymentFailure


@asynccontextmanager
async def lifespan(app: FastAPI):
    await eureka_client.init_async(
        eureka_server="http://eureka-primary:8011/eureka/,http://eureka-secondary:8012/eureka/,http://eureka-tertiary:8013/eureka/",
        app_name="blazebankpaymentservice",
        instance_port=8000,
        instance_host="localhost"
    )
    yield


app = FastAPI(lifespan=lifespan)
payment = PaymentService()


@app.post("/payment/completePayment")
async def completePayment(payment_info: PaymentInformation) -> PaymentSuccess | PaymentFailure:
    return payment.completePayment(payment_info)
