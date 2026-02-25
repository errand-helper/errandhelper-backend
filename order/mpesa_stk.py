import base64

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from .models import MpesaTransaction
from .models import Errand
from .models import Escrow
from django.core.cache import cache


class PaymentAlreadyCompletedError(ValueError):
    pass


class PaymentInProgressError(ValueError):
    def __init__(self, message: str, checkout_request_id: str | None = None):
        super().__init__(message)
        self.checkout_request_id = checkout_request_id


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
        with transaction.atomic():
            locked_errand = Errand.objects.select_for_update().get(id=errand.id)

            already_paid = (
                locked_errand.paid
                or locked_errand.status in {"held", "released"}
                or Escrow.objects.filter(errand=locked_errand).exists()
                or MpesaTransaction.objects.filter(
                    errand=locked_errand,
                    direction="inbound",
                    status="success",
                ).exists()
            )
            if already_paid:
                raise PaymentAlreadyCompletedError(
                    "This errand is already paid. You cannot pay twice."
                )

            active_txn = (
                MpesaTransaction.objects
                .filter(errand=locked_errand, direction="inbound", status="initiated")
                .order_by("-createdAt")
                .first()
            )
            if active_txn:
                raise PaymentInProgressError(
                    "A payment request is already in progress for this errand.",
                    checkout_request_id=active_txn.checkout_request_id,
                )

            mpesa_txn = MpesaTransaction.objects.create(
                errand=locked_errand,
                phoneNumber=phone_number,
                amount=amount,
                direction="inbound",
                status="initiated",
            )

        password, timestamp = self._password()

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
            "AccountReference": locked_errand.reference_number,
            "TransactionDesc": f"Errand {locked_errand.reference_number}",
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

        mpesa_txn.checkout_request_id = (data.get("CheckoutRequestID") or data.get("checkout_request_id"))
        # merchantRequestID was removed from the model; keep raw response for tracing.
        mpesa_txn.rawCallback = data
        mpesa_txn.save(update_fields=["checkout_request_id", "rawCallback"])

        locked_errand.status = "pending"
        locked_errand.save(update_fields=["status"])

        return data
    





    def _query_remote_status(self, checkout_id: str) -> dict:
        password, timestamp = self._password()
        token = cache.get("mpesa_access_token") or self._get_access_token()

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_id,
        }

        try:
            response = requests.post(
                f"{self.base_url}/mpesa/stkpushquery/v1/query",
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                timeout=30,
            )
        except requests.RequestException as e:
            raise ValueError(f"Failed to query M-Pesa status: {str(e)}")

        if not response.ok:
            raise ValueError(
                f"Failed to query M-Pesa status. "
                f"Status: {response.status_code}, Body: {response.text[:500]}"
            )

        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            raise ValueError(
                "Failed to decode M-Pesa status response. "
                f"Status: {response.status_code}, Body: {response.text[:500]}"
            )

    def _extract_result_fields(self, raw_payload: dict | None) -> tuple[str | None, str | None]:
        if not raw_payload:
            return None, None

        # Prefer last query payload when present.
        query_payload = raw_payload.get("last_query_response")
        if isinstance(query_payload, dict):
            code = query_payload.get("ResultCode")
            desc = query_payload.get("ResultDesc")
            if code is not None or desc is not None:
                return (
                    str(code).strip() if code is not None else None,
                    str(desc).strip() if desc is not None else None,
                )

        # Fallback to callback payload.
        callback = raw_payload.get("Body", {}).get("stkCallback", {})
        code = callback.get("ResultCode")
        desc = callback.get("ResultDesc")
        return (
            str(code).strip() if code is not None else None,
            str(desc).strip() if desc is not None else None,
        )

    def query_status(self, checkout_id: str) -> dict:
        if not checkout_id:
            return {
                "status": "error",
                "detail": "checkout_request_id is required",
            }

        try:
            txn = MpesaTransaction.objects.get(checkout_request_id=checkout_id)
        except MpesaTransaction.DoesNotExist:
            return {
                "status": "not_found",
                "checkout_request_id": checkout_id,
            }

        query_payload = {}
        if txn.status == "initiated":
            query_payload = self._query_remote_status(checkout_id)

            raw_payload = txn.rawCallback or {}
            raw_payload["last_query_response"] = query_payload
            txn.rawCallback = raw_payload

            # Query can safely conclude hard failures; success is finalized by callback.
            result_code = str(query_payload.get("ResultCode", "")).strip()
            if result_code and result_code != "0":
                txn.status = "failed"
                txn.save(update_fields=["status", "rawCallback"])
            else:
                txn.save(update_fields=["rawCallback"])

        stored_result_code, stored_result_desc = self._extract_result_fields(txn.rawCallback)
        result_code = (
            str(query_payload.get("ResultCode")).strip()
            if query_payload.get("ResultCode") is not None
            else stored_result_code
        )
        result_desc = (
            str(query_payload.get("ResultDesc")).strip()
            if query_payload.get("ResultDesc") is not None
            else stored_result_desc
        )

        if txn.status == "success":
            payment_status = "success"
        elif txn.status == "failed":
            payment_status = "cancelled" if result_code == "1032" else "failed"
        else:
            payment_status = "pending"

        return {
            "status": payment_status,
            "checkout_request_id": txn.checkout_request_id,
            "mpesa_receipt_number": txn.mpesa_receipt_number,
            "amount": str(txn.amount),
            "direction": txn.direction,
            "cancelled": payment_status == "cancelled",
            # Kept for frontend backward compatibility.
            "ResponseCode": "0" if payment_status == "success" else None,
            "ResultCode": (
                "0"
                if payment_status == "success"
                else result_code
            ),
            "ResultDesc": (
                "The service request is processed successfully."
                if payment_status == "success"
                else result_desc
            ),
        }




