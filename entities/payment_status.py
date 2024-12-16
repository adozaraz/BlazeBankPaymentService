from pydantic import BaseModel


class PaymentInformationStatus(BaseModel):
    status: str
    description: str
