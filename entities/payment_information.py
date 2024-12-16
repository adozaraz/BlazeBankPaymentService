from pydantic import BaseModel


class PaymentInformation(BaseModel):
    senderCardNumber: str
    senderAccountNumber: str | None = None
    amount: int
    receiverCardNumber: str
    receiverAccountNumber: str | None = None
    cvv: str | None = None
