import base64
import os
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.utils import timezone
from .models import MpesaTransaction
from .models import Errand
from django.core.cache import cache



# load_dotenv()

# CONSUMER_KEY = os.getenv("CONSUMER_KEY")
# CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
# MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")
# MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE")
# CALLBACK_URL = os.getenv("CALLBACK_URL")
# MPESA_BASE_URL = os.getenv("MPESA_BASE_URL")


# def generate_access_token():
#     credentials = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
#     encoded = base64.b64encode(credentials.encode()).decode()

#     headers = {"Authorization": f"Basic {encoded}"}
#     response = requests.get(
#         f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials",
#         headers=headers,
#     )

#     try:
#         data = response.json()
#     except ValueError:
#         # M-Pesa sometimes returns non-JSON (e.g. HTML error page) on failure
#         raise ValueError(
#             f"Failed to parse access token response: {response.status_code} {response.text}"
#         )

#     if "access_token" not in data:
#         raise ValueError(
#             f"Failed to get access token: {response.status_code} {response.text}"
#         )

#     return data["access_token"]



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
        """Fetch an OAuth access token from Safaricom.

        Handles:
        - Missing configuration
        - Non-200 responses (surfacing Safaricom error body)
        - Invalid / non-JSON bodies
        """

        credentials = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(
                f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
                headers=headers,
                timeout=15,
            )
        except requests.RequestException as e:
            # Network / DNS / SSL issues etc.
            raise ValueError(f"Failed to connect to M-Pesa token endpoint: {str(e)}")

        # If Safaricom returns a 4xx/5xx, surface the body to help debugging
        if not response.ok:
            snippet = response.text[:500]
            raise ValueError(
                f"Failed to obtain M-Pesa access token. "
                f"Status: {response.status_code}, Body: {snippet}"
            )

        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            raise ValueError(
                "Failed to decode M-Pesa access token response. "
                f"Status: {response.status_code}, Body: {response.text[:500]}"
            )

        access_token = data.get("access_token")
        if not access_token:
            raise ValueError(f"Access token missing in M-Pesa response: {data}")
        
        cache.set("mpesa_access_token", access_token, timeout=3500)

        return access_token


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

        token = self._get_access_token()

        response = requests.post(
            f"{self.base_url}/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
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

        mpesa_txn.checkout_request_id = data.get("checkout_request_id")
        mpesa_txn.merchantRequestID = data.get("MerchantRequestID")
        mpesa_txn.save()

        errand.status = "pending"
        errand.save(update_fields=["status"])

        return data


    def query_status(self, checkout_id: str) -> dict:
        
        if not checkout_id:
            return {
                "status": "error",
                "detail": "checkout_request_id is required",
            }

        try:
            # Use the current snake_case field name that actually exists on the model
            txn = MpesaTransaction.objects.get(checkout_request_id=checkout_id)
        except MpesaTransaction.DoesNotExist:
            # If we don't have a matching transaction, just report not_found
            return {
                "status": "not_found",
                "checkout_request_id": checkout_id,
            }

        checkout_request_id = getattr(txn, "checkout_request_id", None)
        # mpesa_receipt_number = getattr(txn, "mpesa_receipt_number", None)

        return {
            # "status": txn.status,
            "checkout_request_id": checkout_request_id,
            "merchant_request_id": getattr(txn, "merchantRequestID", None),
            # "mpesa_receipt_number": mpesa_receipt_number,
            "amount": str(txn.amount),
            "direction": txn.direction,
            "ResultCode": 0 if txn.status == "success" else 1,
        }









