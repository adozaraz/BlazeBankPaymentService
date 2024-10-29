from entities.payment_information import PaymentInformation
from entities.payment_status import PaymentFailure, PaymentSuccess


class PaymentService:
    def __init__(self):
        pass

    def completePayment(self, payment_information: PaymentInformation) -> PaymentSuccess | PaymentFailure:
        pass
