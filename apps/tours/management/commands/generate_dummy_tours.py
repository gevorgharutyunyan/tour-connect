import random
from datetime import timedelta, datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.tours.models import Tour, TourDate, TourImage
from apps.common.models import Language, Location
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate dummy tour data'

    def add_arguments(self, parser):
        parser.add_argument('--tours', type=int, default=50, help='Number of tours to generate')

    def handle(self, *args, **options):
        # Sample data for generation
        tour_titles = [
            "Historical City Walk", "Mountain Adventure Trek", "Culinary Food Tour",
            "Wine Tasting Experience", "Beach Paradise Tour", "Cultural Heritage Walk",
            "Wildlife Safari Adventure", "Photography Tour", "Local Markets Tour",
            "Ancient Ruins Expedition", "Street Art Discovery", "Sunset Sailing Trip",
            "Forest Hiking Tour", "Urban Legends Walk", "Traditional Crafts Tour",
            "Island Hopping Adventure", "Desert Safari Experience", "River Cruise Journey",
            "Bike City Tour", "Ghost Stories Walk", "Farm to Table Experience",
            "Architecture Discovery", "Village Life Tour", "Cave Exploration",
            "Waterfall Adventure", "Local Brewery Tour", "Spiritual Temple Tour",
            "Adventure Sports Day", "Fishing Village Visit", "Mountain Biking Trail"
        ]

        locations = [
            ("Paris", "FR"), ("Tokyo", "JP"), ("New York", "US"), ("Rome", "IT"),
            ("Barcelona", "ES"), ("Sydney", "AU"), ("London", "GB"), ("Berlin", "DE"),
            ("Amsterdam", "NL"), ("Singapore", "SG"), ("Dubai", "AE"), ("Cairo", "EG"),
            ("Rio de Janeiro", "BR"), ("Cape Town", "ZA"), ("Mumbai", "IN")
        ]

        languages = ["English", "Spanish", "French", "German", "Italian", "Japanese", 
                    "Chinese", "Russian", "Arabic", "Portuguese"]

        difficulties = ["easy", "moderate", "challenging"]

        # Create languages if they don't exist
        created_languages = []
        for lang in languages:
            language, _ = Language.objects.get_or_create(name=lang)
            created_languages.append(language)

        # Create locations if they don't exist
        created_locations = []
        for loc_name, country_code in locations:
            location, _ = Location.objects.get_or_create(
                name=loc_name,
                defaults={'country': country_code}
            )
            created_locations.append(location)

        # Get or create guide users
        guide_usernames = ["guide1", "guide2", "guide3", "guide4", "guide5"]
        guides = []
        for username in guide_usernames:
            guide, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'user_type': 'guide'
                }
            )
            if created:
                guide.set_password('password123')
                guide.save()
            guides.append(guide)

        # Generate tours
        num_tours = options['tours']
        for i in range(num_tours):
            # Create tour
            tour = Tour.objects.create(
                guide=random.choice(guides),
                title=f"{random.choice(tour_titles)} #{i+1}",
                description=f"Experience this amazing tour with unique features and unforgettable moments. Tour number {i+1}",
                location=random.choice(created_locations),
                duration=timedelta(hours=random.randint(2, 8)),
                difficulty=random.choice(difficulties),
                max_participants=random.randint(5, 20),
                price=random.randint(50, 500),
                included_services="Guide service, Equipment rental, Refreshments",
                excluded_services="Transportation to meeting point, Personal expenses",
                meeting_point=f"Central location in {random.choice(created_locations).name}",
                cancellation_policy="Free cancellation up to 24 hours before the tour",
                is_active=True
            )

            # Add random languages (2-4 languages per tour)
            tour.languages.set(random.sample(created_languages, random.randint(2, 4)))

            # Create tour dates (3-5 dates per tour)
            for _ in range(random.randint(3, 5)):
                future_date = timezone.now() + timedelta(days=random.randint(1, 60))
                TourDate.objects.create(
                    tour=tour,
                    start_date=future_date.date(),
                    start_time=f"{random.randint(8, 16):02d}:00",
                    available_spots=random.randint(1, tour.max_participants),
                    is_available=True
                )

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_tours} tours')) 