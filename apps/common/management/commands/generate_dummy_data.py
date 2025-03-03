from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker
from apps.accounts.models import Profile
from apps.common.models import Language, Location
from apps.tours.models import Tour, TourDate
from django_countries import countries
import random
from datetime import timedelta, datetime
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates dummy data for testing'

    def __init__(self):
        super().__init__()
        self.fake = Faker()

    def create_languages(self):
        languages = [
            ('English', 'en'), ('Spanish', 'es'), ('French', 'fr'),
            ('German', 'de'), ('Italian', 'it'), ('Chinese', 'zh'),
            ('Japanese', 'ja'), ('Russian', 'ru'), ('Arabic', 'ar'),
            ('Portuguese', 'pt')
        ]
        created_languages = []
        for lang, code in languages:
            language, created = Language.objects.get_or_create(
                name=lang,
                defaults={'code': code}
            )
            created_languages.append(language)
        return created_languages

    def create_locations(self):
        cities = [
            ('New York City', 'US'), ('Paris', 'FR'), ('London', 'GB'),
            ('Tokyo', 'JP'), ('Rome', 'IT'), ('Barcelona', 'ES'),
            ('Berlin', 'DE'), ('Sydney', 'AU'), ('Dubai', 'AE'),
            ('Singapore', 'SG')
        ]
        created_locations = []
        for name, country in cities:
            location, created = Location.objects.get_or_create(
                name=name,
                country=country
            )
            created_locations.append(location)
        return created_locations

    def create_user_and_profile(self, user_type):
        username = self.fake.user_name()
        while User.objects.filter(username=username).exists():
            username = self.fake.user_name()

        user = User.objects.create_user(
            username=username,
            email=self.fake.email(),
            password='testpass123',
            first_name=self.fake.first_name(),
            last_name=self.fake.last_name(),
            user_type=user_type
        )

        # Update the automatically created profile
        profile = user.profile
        profile.phone_number = self.fake.phone_number()
        profile.bio = self.fake.text(max_nb_chars=200)
        profile.date_of_birth = self.fake.date_of_birth(minimum_age=18, maximum_age=80)
        profile.country = random.choice(list(countries))

        # Add random languages
        languages = Language.objects.all()
        profile.languages.set(random.sample(list(languages), random.randint(1, 3)))

        if user_type == 'guide':
            profile.is_verified = random.choice([True, False])
            if profile.is_verified:
                profile.guide_license_number = f"GL{self.fake.random_number(digits=6)}"
                profile.years_of_experience = random.randint(1, 20)

        profile.save()
        return user

    def create_tours(self, guides, locations):
        tour_titles = [
            "Historical City Walk", "Local Food Tour", "Photography Adventure",
            "Cultural Heritage Tour", "Nature Explorer", "Urban Secrets",
            "Art Gallery Tour", "Street Food Safari", "Architecture Walk",
            "Night Life Experience"
        ]

        difficulties = ['easy', 'moderate', 'challenging']
        durations = ['1-3', '4-6', '7-12', 'full-day', 'multi-day']

        for guide in guides:
            # Create 2-4 tours for each guide
            num_tours = random.randint(2, 4)
            for _ in range(num_tours):
                location = random.choice(locations)
                title = f"{location.name} {random.choice(tour_titles)}"
                
                tour = Tour.objects.create(
                    guide=guide,
                    title=title,
                    description=self.fake.paragraph(nb_sentences=5),
                    location=location.name,
                    duration=random.choice(durations),
                    difficulty=random.choice(difficulties),
                    price=Decimal(random.randint(30, 200)),
                    max_participants=random.randint(4, 15),
                    included_services=self.fake.paragraph(nb_sentences=2),
                    excluded_services=self.fake.paragraph(nb_sentences=2),
                    meeting_point=self.fake.street_address(),
                    cancellation_policy=self.fake.paragraph(nb_sentences=2),
                    latitude=float(self.fake.latitude()),
                    longitude=float(self.fake.longitude())
                )

                # Add languages
                languages = Language.objects.all()
                tour.languages.set(random.sample(list(languages), random.randint(1, 3)))

                # Create tour dates for next 3 months
                start_date = timezone.now().date()
                for _ in range(5):
                    date = start_date + timedelta(days=random.randint(1, 90))
                    start_time = datetime.strptime(f"{random.randint(8,18)}:00", "%H:%M").time()
                    max_spots = tour.max_participants
                    
                    TourDate.objects.create(
                        tour=tour,
                        start_date=date,
                        start_time=start_time,
                        max_spots=max_spots,
                        booked_spots=0
                    )

    def handle(self, *args, **kwargs):
        # Create basic data
        self.stdout.write('Creating languages...')
        languages = self.create_languages()
        
        self.stdout.write('Creating locations...')
        locations = self.create_locations()

        # Create users and profiles
        self.stdout.write('Creating users and profiles...')
        
        # Create tourists
        tourists = []
        for _ in range(20):
            tourist = self.create_user_and_profile('tourist')
            tourists.append(tourist)
            
        # Create guides
        guides = []
        for _ in range(10):
            guide = self.create_user_and_profile('guide')
            guides.append(guide)

        # Create tours
        self.stdout.write('Creating tours...')
        self.create_tours(guides, locations)

        self.stdout.write(self.style.SUCCESS('Successfully generated dummy data')) 