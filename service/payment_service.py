import logging
import requests
import json

from entities.payment_information import PaymentInformation
from entities.payment_status import PaymentInformationStatus

from configs.config import get_config

class PaymentService:
    def __init__(self):
        self.logger = logging.getLogger('uvicorn.error')
        self.global_config = get_config()

    def completePayment(self, payment_information: PaymentInformation, token: str) -> PaymentInformationStatus:
        self.logger.debug(f"Payment Information: {payment_information}")

        headers = {'Authorization': f"Bearer {token}", 'Content-Type': 'application/json'}

        if payment_information is None:
            self.logger.error("Payment information cannot be None")
            return PaymentInformationStatus(status='404', description='Нет информации о платеже')

        if payment_information.cvv is None and payment_information.amount > 1500:
            self.logger.error("Payment information cannot be None")
            return PaymentInformationStatus(status='404', description='Ошибка авторизации платежа. Отсутствует CVV код')

        checkIfSenderExists = requests.get(f'{self.global_config["card_service_url"]}/card/check', params={
            'cardNumber': payment_information.senderCardNumber,
            'accountNumber': payment_information.senderAccountNumber
        }, headers=headers)

        checkIfSenderExists = checkIfSenderExists.json()

        checkIfReceiverExists = requests.get(f'{self.global_config["card_service_url"]}/card/check', params={
            'cardNumber': payment_information.receiverCardNumber,
            'accountNumber': payment_information.receiverAccountNumber
        }, headers=headers)

        checkIfReceiverExists = checkIfReceiverExists.json()

        self.logger.debug(f"CheckIfSenderExists: {checkIfSenderExists}")
        self.logger.debug(f"CheckIfReceiverExists: {checkIfReceiverExists}")

        if not checkIfSenderExists.get('cardExists') and not checkIfReceiverExists.get('cardExists'):
            return PaymentInformationStatus(status='404', description='Ошибка платежа. Одного из клиентов не существует в системе')

        # Проверка CVV

        senderBalanceUpdate = {
            'balanceChange': -payment_information.amount,
            'accountNumber': payment_information.senderAccountNumber,
            'cardNumber': payment_information.senderCardNumber
        }

        receiverBalanceUpdate = {
            'balanceChange': payment_information.amount,
            'accountNumber': payment_information.receiverAccountNumber,
            'cardNumber': payment_information.receiverCardNumber
        }

        senderStatus = requests.post(f'{self.global_config["card_service_url"]}/card/balance/update', data=json.dumps(senderBalanceUpdate), headers=headers)
        senderStatus = senderStatus.json()

        self.logger.debug(f'senderStatus: {senderStatus}')

        if senderStatus.get('status') != 200:
            self.logger.error('Balance cannot be updated!')
            return PaymentInformationStatus(status='500', description=senderStatus.get('description'))

        receiverStatus = requests.post(f'{self.global_config["card_service_url"]}/card/balance/update', data=json.dumps(receiverBalanceUpdate), headers=headers)
        receiverStatus = receiverStatus.json()

        self.logger.debug(f'receiverStatus: {receiverStatus}')

        if receiverStatus.get('status') != 200:
            self.logger.error('Balance cannot be updated!')
            senderStatus = requests.post(f'{self.global_config["card_service_url"]}/card/balance/update', data=json.dumps(receiverBalanceUpdate), headers=headers)
            return PaymentInformationStatus(status='500', description=receiverStatus.get('description'))

        # Внести в БД операцию

        return PaymentInformationStatus(status='200', description='Операция завершена успешно')


