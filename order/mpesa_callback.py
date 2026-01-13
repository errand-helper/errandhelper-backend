from django.db import transaction
from .models import MpesaTransaction, Escrow
from .models import Wallet, WalletTransaction


class MpesaCallbackService:
    @transaction.atomic
    def process_stk_callback(self, payload: dict):
        callback = payload["Body"]["stkCallback"]
        checkout_id = callback["CheckoutRequestID"]
        result_code = callback["ResultCode"]

        mpesa_txn = MpesaTransaction.objects.select_for_update().get(
            checkout_request_id=checkout_id
        )

        mpesa_txn.raw_callback = payload

        if result_code != 0:
            mpesa_txn.status = "failed"
            mpesa_txn.save()
            return

        metadata = callback["CallbackMetadata"]["Item"]
        amount = next(i["Value"] for i in metadata if i["Name"] == "Amount")
        receipt = next(i["Value"] for i in metadata if i["Name"] == "MpesaReceiptNumber")

        mpesa_txn.amount = amount
        mpesa_txn.mpesa_receipt_number = receipt
        mpesa_txn.status = "success"
        mpesa_txn.save()

        errand = mpesa_txn.errand

        Escrow.objects.create(
            errand=errand,
            amount=amount,
        )

        platform_wallet = Wallet.objects.select_for_update().get(owner_type="platform")

        WalletTransaction.objects.create(
            wallet=platform_wallet,
            errand=errand,
            amount=amount,
            transaction_type="hold",
            reference=receipt,
        )

        platform_wallet.locked_balance += amount
        platform_wallet.save()

        errand.status = "funds_held"
        errand.save(update_fields=["status"])



































# from django.db import transaction
# from .models import MpesaTransaction, Escrow
# from .models import Wallet, WalletTransaction


# class MpesaCallbackService:
#     @transaction.atomic
#     def handle_stk_callback(self, payload: dict):
#         callback = payload["Body"]["stkCallback"]
#         checkout_id = callback["CheckoutRequestID"]

#         mpesa_txn = (
#             MpesaTransaction.objects
#             .select_for_update()
#             .get(checkout_request_id=checkout_id)
#         )

#         # Idempotency guard
#         if mpesa_txn.status == "success":
#             return

#         mpesa_txn.raw_callback = payload

#         if callback["ResultCode"] != 0:
#             mpesa_txn.status = "failed"
#             mpesa_txn.save(update_fields=["status", "raw_callback"])
#             return

#         metadata = {
#             item["Name"]: item.get("Value")
#             for item in callback["CallbackMetadata"]["Item"]
#         }

#         mpesa_txn.mpesa_receipt_number = metadata.get("MpesaReceiptNumber")
#         mpesa_txn.status = "success"
#         mpesa_txn.save(update_fields=["status", "mpesa_receipt_number", "raw_callback"])

#         errand = mpesa_txn.errand

#         escrow = Escrow.objects.create(
#             errand=errand,
#             amount=mpesa_txn.amount,
#         )

#         platform_wallet = Wallet.objects.select_for_update().get(owner_type="platform")

#         WalletTransaction.objects.create(
#             wallet=platform_wallet,
#             errand=errand,
#             amount=mpesa_txn.amount,
#             transaction_type="hold",
#             reference=mpesa_txn.mpesa_receipt_number,
#         )

#         platform_wallet.locked_balance += mpesa_txn.amount
#         platform_wallet.save(update_fields=["locked_balance"])

#         errand.status = "funds_held"
#         errand.save(update_fields=["status"])
