from django.db import transaction
from .models import MpesaTransaction, Escrow
from .models import Wallet, WalletTransaction


class MpesaCallbackService:
    @transaction.atomic
    def process_stk_callback(self, payload: dict):

        try:
            callback = payload["Body"]["stkCallback"]
            checkout_id = callback["checkout_request_id"]
            result_code = callback["ResultCode"]
        except KeyError:
            raise ValueError("Invalid M-Pesa callback payload")

        mpesa_txn = (
            MpesaTransaction.objects
            .select_for_update()
            .get(checkout_request_id=checkout_id)
        )

        # Idempotency guard
        if mpesa_txn.status == "success":
            return

        mpesa_txn.raw_callback = payload

        if result_code != 0:
            mpesa_txn.status = "failed"
            mpesa_txn.save(update_fields=["status", "raw_callback"])
            return

        metadata = callback.get("CallbackMetadata", {}).get("Item", [])

        def get_meta(name):
            return next(
                (item["Value"] for item in metadata if item["Name"] == name),
                None
            )

        amount = get_meta("Amount")
        receipt = get_meta("MpesaReceiptNumber")

        if not receipt:
            raise ValueError("Missing M-Pesa receipt number")

        mpesa_txn.amount = amount
        mpesa_txn.mpesa_receipt_number = receipt
        mpesa_txn.status = "success"
        mpesa_txn.save()

        errand = mpesa_txn.errand

        # ---- Escrow Creation (idempotent) ----
        escrow, created = Escrow.objects.get_or_create(
            errand=errand,
            defaults={"amount": amount}
        )

        if not created:
            return

        # ---- Platform Wallet Hold ----
        platform_wallet = Wallet.objects.select_for_update().get(
            owner_type="platform"
        )

        WalletTransaction.objects.create(
            wallet=platform_wallet,
            errand=errand,
            amount=amount,
            transaction_type="hold",
            reference=receipt,
        )

        platform_wallet.locked_balance += amount
        platform_wallet.save(update_fields=["locked_balance"])

        errand.status = "funds_held"
        errand.save(update_fields=["status"])
























# class MpesaCallbackService:
#     @transaction.atomic
#     def process_stk_callback(self, payload: dict):
#         callback = payload["Body"]["stkCallback"]
#         checkout_id = callback["CheckoutRequestID"]
#         result_code = callback["ResultCode"]

#         mpesa_txn = MpesaTransaction.objects.select_for_update().get(
#             checkout_request_id=checkout_id
#         )

#         mpesa_txn.raw_callback = payload

#         if result_code != 0:
#             mpesa_txn.status = "failed"
#             mpesa_txn.save()
#             return

#         metadata = callback["CallbackMetadata"]["Item"]
#         amount = next(i["Value"] for i in metadata if i["Name"] == "Amount")
#         receipt = next(i["Value"] for i in metadata if i["Name"] == "MpesaReceiptNumber")

#         mpesa_txn.amount = amount
#         mpesa_txn.mpesa_receipt_number = receipt
#         mpesa_txn.status = "success"
#         mpesa_txn.save()

#         errand = mpesa_txn.errand

#         Escrow.objects.create(
#             errand=errand,
#             amount=amount,
#         )

#         platform_wallet = Wallet.objects.select_for_update().get(owner_type="platform")

#         WalletTransaction.objects.create(
#             wallet=platform_wallet,
#             errand=errand,
#             amount=amount,
#             transaction_type="hold",
#             reference=receipt,
#         )

#         platform_wallet.locked_balance += amount
#         platform_wallet.save()

#         errand.status = "funds_held"
#         errand.save(update_fields=["status"])

































