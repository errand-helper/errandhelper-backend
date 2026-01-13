import base64
from urllib.parse import urlparse

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
        """Fetch an OAuth access token from Safaricom.

        Handles:
        - Missing configuration
        - Non-200 responses (surfacing Safaricom error body)
        - Invalid / non-JSON bodies
        """

        # Fail fast if configuration is missing
        # if not self.base_url:
        #     raise ValueError("MPESA_BASE_URL is not configured. Check your environment variables.")
        # if not self.consumer_key or not self.consumer_secret:
        #     raise ValueError(
        #         "M-Pesa consumer credentials are not configured. "
        #         "Set MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET in your environment."
        #     )

        # parsed = urlparse(self.base_url)
        # if not parsed.scheme or not parsed.netloc:
        #     raise ValueError(
        #         "MPESA_BASE_URL is invalid. Expected something like 'https://sandbox.safaricom.co.ke', "
        #         f"got {self.base_url!r}."
        #     )
        # if parsed.path not in ("", "/") or parsed.query or parsed.params:
        #     raise ValueError(
        #         "MPESA_BASE_URL must NOT include path or query parameters. "
        #         "Use only the base domain, e.g. 'https://sandbox.safaricom.co.ke'. "
        #         f"Current value: {self.base_url!r}"
        #     )

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
    


    # def query_status(self, checkout_id: str) -> dict:
    #     """Return the status of an STK push for the given CheckoutRequestID.

    #     This implementation relies on the MpesaTransaction record that was
    #     created when the STK push was initiated and (optionally) updated by
    #     the callback handler. It does **not** call Safaricom's query API, but
    #     simply exposes what we currently know in our database.
    #     """
    #     if not checkout_id:
    #         return {
    #             "status": "error",
    #             "detail": "checkout_request_id is required",
    #         }

    #     try:
    #         txn = MpesaTransaction.objects.get(checkoutRequestID=checkout_id)
    #     except MpesaTransaction.DoesNotExist:
    #         return {
    #             "status": "not_found",
    #             "checkout_request_id": checkout_id,
    #         }

    #     return {
    #         "status": txn.status,
    #         "checkout_request_id": txn.checkoutRequestID,
    #         "merchant_request_id": txn.merchantRequestID,
    #         "mpesa_receipt_number": txn.mpesaReceiptNumber,
    #         "amount": str(txn.amount),
    #         "direction": txn.direction,
    #     }









