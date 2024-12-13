from pydantic import BaseModel


class PaymentInformation(BaseModel):
    senderCardNumber: str
    senderAccountNumber: str | None = None
    amount: int
    currency: str
    receiverCardNumber: str
    receiverAccountNumber: str | None = None
    cvv: str | None = None
