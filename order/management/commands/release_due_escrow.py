from django.core.management.base import BaseCommand

from order.payments.escrow_release import EscrowReleaseService


class Command(BaseCommand):
    help = "Release escrow funds automatically for completed errands older than 4 hours."

    def handle(self, *args, **options):
        service = EscrowReleaseService()
        summary = service.release_due_escrows()

        self.stdout.write(
            self.style.SUCCESS(
                "Checked: {checked}, Released: {released}".format(
                    checked=summary["checked"],
                    released=summary["released"],
                )
            )
        )
