import base64
import requests
from django.conf import settings
from django.utils import timezone
from .models import MpesaTransaction
from .models import Errand


class MpesaSTKService:
    def __init__(self):
        self.base_url = settings.MPESA_BASE_URL
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.callback_url = settings.CALLBACK_URL
        self.consumer_key = settings.CONSUMER_KEY
        self.consumer_secret = settings.CONSUMER_SECRET

    def _password(self):
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        raw = f"{self.shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(raw.encode()).decode(), timestamp

    def _get_access_token(self):
        credentials = f"{self.consumer_key}:{self.consumer_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()

        response = requests.get(
            f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
            headers={"Authorization": f"Basic {encoded}"},
            timeout=30,
        )
        
        response.raise_for_status()
        
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            raise ValueError(f"Failed to decode M-Pesa access token response. Status: {response.status_code}, Body: {response.text}")

        if "access_token" not in data:
            raise ValueError(f"Access token missing in M-Pesa response: {data}")

        return data["access_token"]

    def initiate_payment(self, *, errand: Errand, phone_number: str, amount: float):
        password, timestamp = self._password()

        mpesa_txn = MpesaTransaction.objects.create(
            errand=errand,
            phoneNumber=phone_number,
            amount=amount,
            direction="inbound",
            status="initiated",
        )

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": self.callback_url,
            "AccountReference": errand.reference_number,
            "TransactionDesc": f"Errand {errand.reference_number}",
        }

        response = requests.post(
            f"{self.base_url}/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers={
                "Authorization": f"Bearer {self._get_access_token()}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        
        response.raise_for_status()
        
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            mpesa_txn.status = "failed"
            mpesa_txn.save(update_fields=["status"])
            raise ValueError(f"Failed to decode M-Pesa STK push response. Status: {response.status_code}, Body: {response.text}")

        mpesa_txn.checkoutRequestID = data.get("CheckoutRequestID")
        mpesa_txn.merchantRequestID = data.get("MerchantRequestID")
        mpesa_txn.save()

        errand.status = "awaiting_payment"
        errand.save(update_fields=["status"])

        return data









































# import base64
# import requests
# import re
# from django.conf import settings
# from django.utils import timezone
# from .models import MpesaTransaction
# from .models import Errand


# class MpesaSTKService:
#     def __init__(self):
#         self.base_url = settings.MPESA_BASE_URL
#         self.shortcode = settings.MPESA_SHORTCODE
#         self.passkey = settings.MPESA_PASSKEY
#         self.callback_url = settings.MPESA_CALLBACK_URL
#         self.consumer_key = settings.CONSUMER_KEY
#         self.consumer_secret = settings.CONSUMER_SECRET

#     # -----------------------
#     # Utilities
#     # -----------------------

#     def format_phone(self, phone: str) -> str:
#         phone = phone.replace("+", "")
#         if re.match(r"^254\d{9}$", phone):
#             return phone
#         if phone.startswith("0") and len(phone) == 10:
#             return f"254{phone[1:]}"
#         raise ValueError("Invalid phone number format")

#     def _password(self):
#         timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
#         data = f"{self.shortcode}{self.passkey}{timestamp}"
#         password = base64.b64encode(data.encode()).decode()
#         return password, timestamp

#     def _get_access_token(self) -> str:
#         credentials = f"{self.consumer_key}:{self.consumer_secret}"
#         encoded = base64.b64encode(credentials.encode()).decode()

#         headers = {
#             "Authorization": f"Basic {encoded}",
#             "Content-Type": "application/json",
#         }

#         response = requests.get(
#             f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
#             headers=headers,
#             timeout=15,
#         )
#         response.raise_for_status()

#         data = response.json()
#         if "access_token" not in data:
#             raise ValueError("Access token missing in M-Pesa response")

#         return data["access_token"]

#     # -----------------------
#     # STK Push
#     # -----------------------

#     def initiate_payment(self, *, errand: Errand, phone_number: str, amount: float):
#         phone_number = self.format_phone(phone_number)
#         password, timestamp = self._password()

#         mpesa_txn = MpesaTransaction.objects.create(
#             errand=errand,
#             phone_number=phone_number,
#             amount=amount,
#             direction="inbound",
#             status="initiated",
#         )

#         payload = {
#             "BusinessShortCode": self.shortcode,
#             "Password": password,
#             "Timestamp": timestamp,
#             "TransactionType": "CustomerPayBillOnline",
#             "Amount": int(amount),
#             "PartyA": phone_number,
#             "PartyB": self.shortcode,
#             "PhoneNumber": phone_number,
#             "CallBackURL": self.callback_url,
#             "AccountReference": errand.reference_number,
#             "TransactionDesc": f"Errand {errand.reference_number}",
#         }

#         headers = {
#             "Authorization": f"Bearer {self._get_access_token()}",
#             "Content-Type": "application/json",
#         }

#         response = requests.post(
#             f"{self.base_url}/mpesa/stkpush/v1/processrequest",
#             json=payload,
#             headers=headers,
#             timeout=30,
#         )
#         response.raise_for_status()

#         data = response.json()

#         mpesa_txn.checkout_request_id = data.get("CheckoutRequestID")
#         mpesa_txn.merchant_request_id = data.get("MerchantRequestID")
#         mpesa_txn.save(update_fields=["checkout_request_id", "merchant_request_id"])

#         errand.status = "awaiting_payment"
#         errand.save(update_fields=["status"])

#         return data
