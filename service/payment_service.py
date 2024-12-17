import logging
import requests
import json
import os

from entities.other_bank_transaction import OtherBankTransaction
from entities.payment_information import PaymentInformation
from entities.payment_status import PaymentInformationStatus
from configs.config import get_config
from service.general_functions import send_message, get_bank_topic, authenticate_in_keycloak, get_service_instance


class PaymentService:
    def __init__(self):
        self.logger = logging.getLogger('uvicorn.error')
        self.global_config = get_config()
        self.master_headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {authenticate_in_keycloak()}"
        }

    def completePayment(self, payment_information: PaymentInformation, token: str) -> PaymentInformationStatus:
        self.logger.debug(f"Payment Information: {payment_information}")

        headers = {'Authorization': f"Bearer {token}", 'Content-Type': 'application/json'}

        if payment_information is None:
            self.logger.error("Payment information cannot be None")
            return PaymentInformationStatus(status='404', description='Нет информации о платеже')

        self.logger.info('Checking the amount and cvv availability')
        if payment_information.cvv is None and payment_information.amount > 1500:
            self.logger.error("Payment information cannot be None")
            return PaymentInformationStatus(status='404', description='Ошибка авторизации платежа. Отсутствует CVV код')

        self.logger.info('Checking if the sender card exists')

        if not self.checkIfCardExists(payment_information.senderCardNumber, payment_information.senderAccountNumber, headers):
            return PaymentInformationStatus(status='404', description='Ошибка платежа. такой карты клиента не существует!')

        if not payment_information.cvv is None:
            self.logger.info('Verifying cvv')
            instance = get_service_instance(self.global_config.get('card_service_name'))

            verifyCvvResult = requests.post(f'{instance}/card/verify/cvv', data=json.dumps({
                'cardNumber': payment_information.senderCardNumber,
                'cvv': payment_information.cvv
            }), headers=headers)
            verifyCvvResult = verifyCvvResult.json()

            self.logger.debug(f'Verify CVV: {verifyCvvResult}')

            if not verifyCvvResult.get('isValid', False):
                return PaymentInformationStatus(status='403', description='Ошибка! Неправильный код CVV. Повторите попытку ещё раз!')

        self.logger.info('Updating sender balance')
        sender_status, sender_error_description = self.commencePayment(payment_information.senderCardNumber,
                                                                       -payment_information.amount, headers)

        self.logger.debug(f'senderStatus: {sender_status}')

        if not sender_status:
            self.logger.error('Balance cannot be updated!')
            return PaymentInformationStatus(status='500', description=sender_error_description)

        if payment_information.receiverBank is None or payment_information.receiverBank == os.environ.get('BANK_NAME', 'BlazeBank'):
            self.logger.info('Updating receiver balance')
            receiver_status, receiver_error_description = self.commencePayment(payment_information.receiverCardNumber, payment_information.amount, headers)

            self.logger.debug(f'receiverStatus: {receiver_status}')

            if not receiver_status:
                self.logger.error('Balance cannot be updated!')
                self.commencePayment(payment_information.senderCardNumber, payment_information.amount, headers)
                return PaymentInformationStatus(status='500', description=receiver_error_description)

            self.logger.info('Payment finished successfully')

            return PaymentInformationStatus(status='200', description='Операция завершена успешно')
        else:
            self.logger.info('Sending info to another bank')

            message = {
                'receiverCardNumber': payment_information.receiverCardNumber,
                'amount': payment_information.amount
            }

            send_message(get_bank_topic(payment_information.receiverBank), message)

            return PaymentInformationStatus(status='202', description='Операция взята в работу и будет завершена в ближайшие рабочие дни')

    def completePaymentFromOtherBank(self, incoming_payment_info: OtherBankTransaction):
        if not self.checkIfCardExists(incoming_payment_info.receiverCardNumber, None, self.master_headers):
            self.logger.error("Payment information cannot be finished!")

        status, error_description = self.commencePayment(incoming_payment_info.receiverCardNumber, incoming_payment_info.amount, self.master_headers)

        if not status:
            self.logger.error("Payment information cannot be finished!")
            self.logger.error(error_description)
        else:
            self.logger.info('Payment finished successfully')

    def commencePayment(self, cardNumber: str, balance_change: float | int, headers: dict) -> tuple[bool, str | None]:
        balanceUpdate = {
            'balanceChange': balance_change,
            'cardNumber': cardNumber
        }

        instance = get_service_instance(self.global_config.get('card_service_name'))
        self.logger.info(f'Updating balance: {balanceUpdate}')
        status = requests.post(f'{instance}/card/balance/update', data=json.dumps(balanceUpdate), headers=headers)
        status = status.json()

        if status.get('status') != 200:
            self.logger.error('Balance cannot be updated!')
            return False, status.get('description')

        self.logger.info('Balance updated')
        return True, None

    def checkIfCardExists(self, cardNumber: str, accountNumber: str | None, headers: dict) -> bool:
        instance = get_service_instance(self.global_config.get('card_service_name'))
        self.logger.info(f'Checking if {cardNumber} exists')
        status = requests.get(f'{instance}/card/check', params={
            'cardNumber': cardNumber,
            'accountNumber': accountNumber
        }, headers=headers)

        status = status.json()

        return status.get('cardExists', False)