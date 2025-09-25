from django.core.management.base import BaseCommand
from faker import Faker
import random
from datetime import timedelta
from django.utils import timezone

from src.apps.user.models import User, Roles
from src.apps.booking.models import Booking
from src.apps.service.models import Service, ServiceType


class Command(BaseCommand):
    help = "Generate fake users and bookings (with bulk_create)"

    def handle(self, *args, **kwargs):
        fake = Faker("uz_UZ")

        barber_role, _ = Roles.objects.get_or_create(name="Barber")
        client_role, _ = Roles.objects.get_or_create(name="Client")
        manager_role, _ = Roles.objects.get_or_create(name="Manager")

        barbers_to_create = []
        for _ in range(5):
            phone = f"+998{random.randint(900000000, 999999999)}"
            barbers_to_create.append(User(
                phone_number=phone,
                first_name=fake.first_name(),
                telegram_id=random.randint(10000, 99999),
                language="uz"
            ))
        User.objects.bulk_create(barbers_to_create, ignore_conflicts=True)
        barbers = list(User.objects.filter(phone_number__in=[b.phone_number for b in barbers_to_create]))
        for b in barbers:
            b.set_password("12345")
            b.save(update_fields=["password"])
            b.roles.add(barber_role)

        self.stdout.write(self.style.SUCCESS(f"Created {len(barbers)} Barbers"))

        managers_to_create = []
        for _ in range(2):
            phone = f"+998{random.randint(900000000, 999999999)}"
            managers_to_create.append(User(
                phone_number=phone,
                first_name=fake.first_name(),
                telegram_id=random.randint(10000, 99999),
                language="uz"
            ))
        User.objects.bulk_create(managers_to_create, ignore_conflicts=True)
        managers = list(User.objects.filter(phone_number__in=[m.phone_number for m in managers_to_create]))
        for m in managers:
            m.set_password("12345")
            m.save(update_fields=["password"])
            m.roles.add(manager_role)
        self.stdout.write(self.style.SUCCESS(f"Created {len(managers)} Managers"))

        clients_to_create = []
        for _ in range(1000 - 5 - 2):
            phone = f"+998{random.randint(900000000, 999999999)}"
            clients_to_create.append(User(
                phone_number=phone,
                first_name=fake.first_name(),
                telegram_id=random.randint(10000, 99999),
                language="uz"
            ))
        User.objects.bulk_create(clients_to_create, ignore_conflicts=True)
        clients = list(User.objects.filter(phone_number__in=[c.phone_number for c in clients_to_create]))
        for c in clients:
            c.set_password("12345")
            c.save(update_fields=["password"])
            c.roles.add(client_role)

        self.stdout.write(self.style.SUCCESS(f"Created {len(clients)} Clients"))

        service_type_names = ["Haircut", "Beard Trim", "Shave", "Coloring", "Styling"]

        all_service_types = []
        all_services = []
        for barber in barbers:
            for st_name in service_type_names:
                st = ServiceType.objects.create(barber=barber, name=st_name)
                all_service_types.append(st)

                service = Service(
                    service_type=st,
                    name=f"{st_name} by {barber.first_name}",
                    price=random.randint(50000, 200000),
                    duration=timedelta(minutes=random.choice([30, 45, 60])),
                )
                all_services.append(service)

        Service.objects.bulk_create(all_services)
        self.stdout.write(self.style.SUCCESS(
            f"Created {len(all_service_types)} ServiceTypes and {len(all_services)} Services"
        ))


        services = list(Service.objects.select_related("service_type", "service_type__barber"))

        bookings_to_create = []
        for _ in range(10000):
            client = random.choice(clients)
            service = random.choice(services)
            barber = service.service_type.barber

            start_time = timezone.now() + timedelta(
                days=random.randint(1, 10),
                hours=random.randint(9, 17)
            )
            end_time = start_time + timedelta(minutes=service.duration_minutes)

            bookings_to_create.append(Booking(
                user=client,
                barber=barber,
                service=service,
                start_time=start_time,
                end_time=end_time,
                notes=fake.sentence(),
                status=random.choice(list(Booking.BookingStatus.values))
            ))

        Booking.objects.bulk_create(bookings_to_create, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f"Created {len(bookings_to_create)} Bookings"))
