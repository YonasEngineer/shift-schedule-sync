from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from apps.locations.models import Location
# from apps.skills.models import Skill
from apps.users.models.skill import Skill
from apps.users.models.user_skill import UserSkill

from apps.locations.models import UserLocation
from apps.availability.models import AvailabilityRecurring, AvailabilityException

from django.contrib.auth.hashers import make_password
from datetime import date

User = get_user_model()


class Command(BaseCommand):
    help = "Seed database with initial data"

    @transaction.atomic
    def handle(self, *args, **kwargs):

        self.stdout.write("🔥 Cleaning database...")

        # DELETE (order matters because of FK)
        AvailabilityException.objects.all().delete()
        AvailabilityRecurring.objects.all().delete()
        UserSkill.objects.all().delete()
        UserLocation.objects.all().delete()
        User.objects.all().delete()
        Location.objects.all().delete()
        Skill.objects.all().delete()

        self.stdout.write("✅ Database cleaned")

        # =========================
        # 1. SKILLS
        # =========================
        skills = Skill.objects.bulk_create([
            Skill(name='bartender'),
            Skill(name='cook'),
            Skill(name='server'),
            Skill(name='host'),
        ])

        bartender, cook, server, host = Skill.objects.all()

        # =========================
        # 2. LOCATIONS
        # =========================
        sf = Location.objects.create(
            name='Coastal Eats - San Francisco',
            timezone='America/Los_Angeles',
            address='SF Downtown',
        )

        la = Location.objects.create(
            name='Coastal Eats - Los Angeles',
            timezone='America/Los_Angeles',
            address='LA Center',
        )

        ny = Location.objects.create(
            name='Coastal Eats - New York',
            timezone='America/New_York',
            address='Manhattan',
        )

        miami = Location.objects.create(
            name='Coastal Eats - Miami',
            timezone='America/New_York',
            address='Miami Beach',
        )

        # =========================
        # 3. USERS
        # =========================
        password = make_password("Test@123")
        admin = User.objects.create(
            username='admin',
            first_name='System',
            last_name='Admin',
            email='admin@coastal.com',
            password=password,
            role='ADMIN',
        )

        manager_sf = User.objects.create(
            username='alice_sf',
            first_name='Alice',
            last_name='SFManager',
            email='alice@sf.com',
            password=password,
            role='MANAGER',
        )

        manager_ny = User.objects.create(
            username='bob_ny',
            first_name='Bob',
            last_name='NYManager',
            email='bob@ny.com',
            password=password,
            role='MANAGER',
        )

        staff1 = User.objects.create(
            username='john_doe',
            first_name='John',
            last_name='Doe',
            email='john@staff.com',
            password=password,
            role='STAFF',
        )

        staff2 = User.objects.create(
            username='maria_lopez',
            first_name='Maria',
            last_name='Lopez',
            email='maria@staff.com',
            password=password,
            role='STAFF',
        )

        staff3 = User.objects.create(
            username='sarah_kim',
            first_name='Sarah',
            last_name='Kim',
            email='sarah@staff.com',
            password=password,
            role='STAFF',
        )

        staff4 = User.objects.create(
            username='david_chen',
            first_name='David',
            last_name='Chen',
            email='david@staff.com',
            password=password,
            role='STAFF',
        )


# =========================
# 4. USER LOCATIONS
# =========================
        UserLocation.objects.bulk_create([
            # Managers
            UserLocation(user=manager_sf, location=sf,
                         role='MANAGER', is_certified=True),
            UserLocation(user=manager_ny, location=ny,
                         role='MANAGER', is_certified=True),

            # Staff
            UserLocation(user=staff1, location=sf,
                         role='STAFF', is_certified=True),
            UserLocation(user=staff1, location=ny,
                         role='STAFF', is_certified=True),

            UserLocation(user=staff2, location=sf,
                         role='STAFF', is_certified=True),
            UserLocation(user=staff2, location=la,
                         role='STAFF', is_certified=True),

            UserLocation(user=staff3, location=ny,
                         role='STAFF', is_certified=True),
            UserLocation(user=staff3, location=miami,
                         role='STAFF', is_certified=True),

            UserLocation(user=staff4, location=la,
                         role='STAFF', is_certified=True),
            UserLocation(user=staff4, location=sf,
                         role='STAFF', is_certified=True),
        ])


# =========================
# 5. USER SKILLS
# =========================
        UserSkill.objects.bulk_create([
            UserSkill(user=staff1, skill=bartender),
            UserSkill(user=staff1, skill=server),

            UserSkill(user=staff2, skill=server),
            UserSkill(user=staff2, skill=host),

            UserSkill(user=staff3, skill=cook),

            UserSkill(user=staff4, skill=bartender),
            UserSkill(user=staff4, skill=cook),
        ])


# =========================
# 6. AVAILABILITY RECURRING
# =========================
        AvailabilityRecurring.objects.bulk_create([
            AvailabilityRecurring(
                user=staff1,
                day_of_week=6,
                start_time="11:00",
                end_time="18:00",
                timezone="America/Los_Angeles",
            ),
            AvailabilityRecurring(
                user=staff2,
                day_of_week=6,
                start_time="11:00",
                end_time="20:00",
                timezone="America/Los_Angeles",
            ),
            AvailabilityRecurring(
                user=staff3,
                day_of_week=6,
                start_time="21:00",
                end_time="23:00",
                timezone="America/New_York",
            ),
        ])


# =========================
# 7. AVAILABILITY EXCEPTIONS
# =========================
        AvailabilityException.objects.bulk_create([
            AvailabilityException(
                user=staff1,
                date=date(2026, 4, 8),
                start_time="18:00",
                end_time="20:00",
                is_available=False,
            ),
            AvailabilityException(
                user=staff2,
                date=date(2026, 4, 9),
                start_time="14:00",
                end_time="17:00",
                is_available=False,
            ),
        ])

        self.stdout.write(self.style.SUCCESS("🎉 Seed completed successfully!"))
