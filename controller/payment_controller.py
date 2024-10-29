from fastapi import FastAPI

from service.payment_service import PaymentService
from entities.payment_information import PaymentInformation
from entities.payment_status import PaymentSuccess, PaymentFailure

app = FastAPI()
payment = PaymentService()

@app.post("/payment/completePayment")
async def completePayment(payment_info: PaymentInformation) -> PaymentSuccess | PaymentFailure:
    return payment.completePayment(payment_info)
