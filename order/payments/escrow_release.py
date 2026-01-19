# from django.db import transaction
# from django.utils import timezone

# from order.models import Escrow, MpesaTransaction, Payout, Wallet, WalletTransaction
# # from payments.models import Escrow, Payout, MpesaTransaction
# # from wallets.models import Wallet, WalletTransaction
# # from mpesa.services.b2c import MpesaB2CService


# class EscrowReleaseService:
#     @transaction.atomic
#     def release(self, errand):
#         if errand.status != 'verified':
#             raise ValueError("Errand not verified")

#         escrow = Escrow.objects.select_for_update().get(errand=errand)
#         platform_wallet = Wallet.objects.select_for_update().get(owner_type='platform')
#         business_wallet = Wallet.objects.select_for_update().get(
#             owner_type='business',
#             owner=errand.business
#         )

#         b2c = MpesaB2CService()
#         b2c_txn = b2c.send(
#             phone=errand.business.phone,
#             amount=escrow.amount,
#             remarks=f"Errand {errand.reference_number}"
#         )

#         mpesa_txn = MpesaTransaction.objects.create(
#             errand=errand,
#             phone_number=errand.business.phone,
#             amount=escrow.amount,
#             direction='outbound',
#             status='initiated'
#         )

#         WalletTransaction.objects.create(
#             wallet=platform_wallet,
#             errand=errand,
#             amount=escrow.amount,
#             transaction_type='release',
#             reference=mpesa_txn.id
#         )

#         platform_wallet.locked_balance -= escrow.amount
#         platform_wallet.balance -= escrow.amount
#         platform_wallet.save()

#         business_wallet.balance += escrow.amount
#         business_wallet.save()

#         escrow.status = 'released'
#         escrow.released_at = timezone.now()
#         escrow.save()

#         Payout.objects.create(
#             errand=errand,
#             business=errand.business,
#             amount=escrow.amount,
#             mpesa_transaction=mpesa_txn,
#             status='pending'
#         )

#         errand.status = 'paid_out'
#         errand.save(update_fields=['status'])
