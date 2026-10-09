from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.front.models import InactivityNotice


class Command(BaseCommand):
    help = (
        "Delete users that got an inactivity notice "
        "(see `notify_inactive_users`) more than INACTIVITY_CONFIRMATION_PERIOD_DAYS "
        "ago and didn't confirm their account. Users that logged in again in the "
        "meantime are kept. Run periodically (e.g. daily via cron)."
    )

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model

        now = timezone.now()
        deadline = now - timedelta(days=settings.INACTIVITY_CONFIRMATION_PERIOD_DAYS)
        cutoff = now - timedelta(days=settings.INACTIVITY_NOTICE_THRESHOLD_DAYS)
        user_ids = (
            InactivityNotice.objects.filter(
                confirmed_at__isnull=True, sent_at__lt=deadline
            )
            .values_list("user_id", flat=True)
            .distinct()
        )
        deleted = 0
        for user in get_user_model().objects.filter(pk__in=list(user_ids)):
            if user.last_login is not None and user.last_login >= cutoff:
                continue
            user.delete()
            deleted += 1
        self.stdout.write(self.style.SUCCESS("Deleted %d inactive user(s)." % deleted))
