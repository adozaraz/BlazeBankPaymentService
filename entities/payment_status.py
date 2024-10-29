from pydantic import BaseModel


class PaymentSuccess(BaseModel):
    status: str


class PaymentFailure(BaseModel):
    status: str
    reason: str
