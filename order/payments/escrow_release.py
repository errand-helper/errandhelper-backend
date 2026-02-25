from uuid import uuid4

from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from order.models import (
    Dispute,
    Escrow,
    Errand,
    MpesaTransaction,
    Payout,
    Wallet,
    WalletTransaction,
)


class EscrowReleaseService:
    AUTO_RELEASE_HOURS = 4

    def _repair_missing_escrow_if_possible(self, errand: Errand) -> Escrow:
        escrow = Escrow.objects.select_for_update().filter(errand=errand).first()
        if escrow:
            return escrow

        successful_txn = (
            MpesaTransaction.objects
            .filter(errand=errand, direction="inbound", status="success")
            .order_by("-createdAt")
            .first()
        )
        if not successful_txn:
            raise ValueError(
                "No escrow found for this errand and no successful M-Pesa payment was found."
            )

        escrow = Escrow.objects.create(
            errand=errand,
            amount=successful_txn.amount,
            status="holding",
        )

        platform_wallet, _ = Wallet.objects.select_for_update().get_or_create(
            owner_type="platform",
            owner=None,
            defaults={"balance": 0, "locked_balance": 0},
        )

        hold_reference = (
            successful_txn.mpesa_receipt_number
            or f"HOLD-{errand.reference_number}-{successful_txn.id.hex[:8]}"
        )
        hold_exists = WalletTransaction.objects.filter(
            wallet=platform_wallet,
            reference=hold_reference,
        ).exists()
        if not hold_exists:
            WalletTransaction.objects.create(
                wallet=platform_wallet,
                errand=errand,
                amount=successful_txn.amount,
                transaction_type="hold",
                reference=hold_reference,
            )
            platform_wallet.locked_balance += successful_txn.amount
            platform_wallet.save(update_fields=["locked_balance"])

        errand.paid = True
        if errand.status == "unpaid":
            errand.status = "held"
            errand.save(update_fields=["paid", "status"])
        else:
            errand.save(update_fields=["paid"])

        return escrow

    @transaction.atomic
    def release(self, *, errand: Errand, actor=None, automatic: bool = False) -> dict:
        locked_errand = (
            Errand.objects.select_for_update()
            .select_related("client", "business")
            .get(id=errand.id)
        )

        if not automatic and actor != locked_errand.client:
            raise PermissionError("Only the errand client can release escrow funds.")

        if locked_errand.status != "completed":
            raise ValueError("Errand must be completed before releasing funds.")

        if automatic:
            if not locked_errand.completed_at:
                raise ValueError("Errand completion timestamp is missing.")

            release_due_at = locked_errand.completed_at + timedelta(hours=self.AUTO_RELEASE_HOURS)
            if timezone.now() < release_due_at:
                raise ValueError("Auto-release window has not elapsed yet.")

        if Dispute.objects.filter(errand=locked_errand, status="open").exists():
            raise ValueError("Cannot release funds while there is an open dispute.")

        escrow = self._repair_missing_escrow_if_possible(locked_errand)
        if escrow.status == "released":
            return {
                "status": "already_released",
                "errand_id": str(locked_errand.id),
                "amount": str(escrow.amount),
            }

        if escrow.status != "holding":
            raise ValueError("Escrow is not in a releasable holding state.")

        platform_wallet, _ = Wallet.objects.select_for_update().get_or_create(
            owner_type="platform",
            owner=None,
            defaults={"balance": 0, "locked_balance": 0},
        )
        business_wallet, _ = Wallet.objects.select_for_update().get_or_create(
            owner_type="business",
            owner=locked_errand.business,
            defaults={"balance": 0, "locked_balance": 0},
        )

        amount = escrow.amount

        if platform_wallet.locked_balance < amount:
            raise ValueError("Platform locked balance is lower than escrow amount.")

        release_ref = f"REL-{locked_errand.reference_number}-{uuid4().hex[:8]}"
        credit_ref = f"CR-{locked_errand.reference_number}-{uuid4().hex[:8]}"

        WalletTransaction.objects.create(
            wallet=platform_wallet,
            errand=locked_errand,
            amount=amount,
            transaction_type="release",
            reference=release_ref,
        )
        WalletTransaction.objects.create(
            wallet=business_wallet,
            errand=locked_errand,
            amount=amount,
            transaction_type="credit",
            reference=credit_ref,
        )

        platform_wallet.locked_balance -= amount
        platform_wallet.save(update_fields=["locked_balance"])

        business_wallet.balance += amount
        business_wallet.save(update_fields=["balance"])

        escrow.status = "released"
        escrow.releasedAt = timezone.now()
        escrow.save(update_fields=["status", "releasedAt"])

        payout, created = Payout.objects.get_or_create(
            errand=locked_errand,
            business=locked_errand.business,
            defaults={
                "amount": amount,
                "status": "success",
            },
        )
        if not created and payout.status != "success":
            payout.status = "success"
            payout.amount = amount
            payout.save(update_fields=["status", "amount"])

        locked_errand.status = "released"
        locked_errand.save(update_fields=["status"])

        return {
            "status": "released",
            "errand_id": str(locked_errand.id),
            "amount": str(amount),
            "business_id": str(locked_errand.business.id),
        }

    def release_due_escrows(self) -> dict:
        cutoff = timezone.now() - timedelta(hours=self.AUTO_RELEASE_HOURS)
        due_escrows = (
            Escrow.objects.select_related("errand")
            .filter(
                status="holding",
                errand__status="completed",
                errand__completed_at__isnull=False,
                errand__completed_at__lte=cutoff,
            )
            .order_by("errand__completed_at")
        )

        released_errand_ids = []
        for escrow in due_escrows:
            try:
                result = self.release(errand=escrow.errand, automatic=True)
                released_errand_ids.append(result["errand_id"])
            except ValueError:
                # Skip records that are no longer releasable by the time we process them.
                continue

        return {
            "checked": due_escrows.count(),
            "released": len(released_errand_ids),
            "released_errand_ids": released_errand_ids,
        }
