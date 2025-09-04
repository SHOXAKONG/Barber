from django.core.management import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask

class Command(BaseCommand):
    help = "Sync Celery Beat periodic tasks to DB"

    def handle(self, *args, **kwargs):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute="*",
            hour="*",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
            timezone="Asia/Tashkent",
        )
        PeriodicTask.objects.update_or_create(
            name="update-bookings-every-minute",
            defaults={
                "task": "src.apps.booking.tasks.update_completed_bookings",
                "crontab": schedule,
                "enabled": True,
            },
        )
        self.stdout.write(self.style.SUCCESS("Beat tasks synced."))
