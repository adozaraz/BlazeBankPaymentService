import requests
import json

from entities.payment_information import PaymentInformation
from entities.payment_status import PaymentFailure, PaymentSuccess


class PaymentService:
    def __init__(self):
        pass

    def completePayment(self, payment_information: PaymentInformation) -> PaymentSuccess | PaymentFailure:
        if payment_information is None:
            return PaymentFailure(status='1', reason='Нет информации о платеже')

        if payment_information.cvv is None and payment_information.amount > 1500:
            return PaymentFailure(status='2', reason='Ошибка авторизации платежа. Отсутствует CVV код')

        api_url = 'card_service_url'

        checkIfSenderExists = requests.get(f'{api_url}/check', params={
            'cardNumber': payment_information.senderCardNumber,
            'accountNumber': payment_information.senderAccountNumber
        })

        checkIfSenderExists = checkIfSenderExists.json()

        checkIfReceiverExists = requests.get(f'{api_url}/check', params={
            'cardNumber': payment_information.receiverCardNumber,
            'accountNumber': payment_information.receiverAccountNumber
        })

        checkIfReceiverExists = checkIfReceiverExists.json()

        if not checkIfSenderExists.cardExists and checkIfReceiverExists.cardExists:
            return PaymentFailure(status='2', reason='Ошибка платежа. Одного из клиентов не существует в системе')

        # Проверка CVV

        senderBalanceUpdate = {
            'balanceChange': -payment_information.amount,
            'accountNumber': payment_information.senderAccountNumber,
            'cardNumber': payment_information.senderCardNumber
        }

        senderBalanceUpdate = {
            'balanceChange': payment_information.amount,
            'accountNumber': payment_information.receiverAccountNumber,
            'cardNumber': payment_information.receiverCardNumber
        }

        senderStatus = requests.post(f'{api_url}/balance/update', data=json.dumps(senderBalanceUpdate))
        senderStatus = senderStatus.json()

        if senderStatus.status != '0':
            return PaymentFailure(status=senderStatus.status, reason=senderStatus.errorDescription)

        receiverStatus = requests.post(f'{api_url}/balance/update', data=json.dumps(senderBalanceUpdate))
        receiverStatus = receiverStatus.json()

        if receiverStatus.status != '0':
            senderBalanceUpdate['balanceChange'] = payment_information.amount
            senderStatus = requests.post(f'{api_url}/balance/update', data=json.dumps(senderBalanceUpdate))
            return PaymentFailure(status=receiverStatus.status, reason=receiverStatus.errorDescription)

        # Внести в БД операцию

        return PaymentSuccess(status='0')


