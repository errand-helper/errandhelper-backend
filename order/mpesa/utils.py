import base64
import requests
from datetime import datetime
from django.conf import settings


def generate_access_token():
    consumer_key = settings.CONSUMER_KEY
    consumer_secret = settings.CONSUMER_SECRET

    # Choose environment
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    # url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    encoded_credentials = base64.b64encode(
        f"{consumer_key}:{consumer_secret}".encode()
    ).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()["access_token"]


def send_stk_push(phone_number, amount, account_reference="account"):
    token = generate_access_token()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    short_code = settings.MPESA_SHORTCODE
    passkey = settings.MPESA_PASSKEY

    password = base64.b64encode(
        f"{short_code}{passkey}{timestamp}".encode()
    ).decode()

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    # url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": short_code,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": "STK Push Payment"
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    return response.json()
