from pydantic import BaseModel


class OtherBankTransaction(BaseModel):
    receiverCardNumber: str
    amount: float | int