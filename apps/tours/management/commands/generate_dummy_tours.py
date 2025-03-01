import random
from datetime import timedelta, datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.tours.models import Tour, TourDate, TourImage
from apps.common.models import Language, Location
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate dummy tours for testing'

    def handle(self, *args, **options):
        # Delete existing tours
        Tour.objects.all().delete()

        # Create languages if they don't exist
        language_data = [
            ('English', 'en'),
            ('Spanish', 'es'),
            ('French', 'fr'),
            ('German', 'de'),
            ('Italian', 'it'),
            ('Japanese', 'ja'),
            ('Chinese', 'zh'),
            ('Russian', 'ru'),
        ]

        created_languages = []
        for name, code in language_data:
            language, created = Language.objects.get_or_create(
                name=name,
                defaults={'code': code}
            )
            created_languages.append(language)

        # Create guide users if they don't exist
        guide_names = ['John Smith', 'Maria Garcia', 'Hans Weber', 'Sophie Martin']
        created_guides = []
        
        for name in guide_names:
            username = name.lower().replace(' ', '_')
            email = f"{username}@example.com"
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': name.split()[0],
                    'last_name': name.split()[1],
                    'user_type': 'guide'
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
            
            created_guides.append(user)

        # Tour titles
        tour_titles = [
            "Historical City Walk",
            "Food and Wine Tour",
            "Street Art Discovery",
            "Local Markets Tour",
            "Architecture Photography Tour",
            "Hidden Gems Walking Tour",
            "Cultural Heritage Experience",
            "Urban Legends Tour",
            "Sunset City Views",
            "Traditional Crafts Workshop"
        ]

        # Locations
        locations = [
            ('Paris', 'France'),
            ('Rome', 'Italy'),
            ('Barcelona', 'Spain'),
            ('Berlin', 'Germany'),
            ('Amsterdam', 'Netherlands'),
            ('Prague', 'Czech Republic'),
            ('Vienna', 'Austria'),
            ('London', 'UK')
        ]

        # Create tours
        for _ in range(20):
            location = random.choice(locations)
            duration_choices = ['1-3', '4-6', '7-12', 'full-day', 'multi-day']
            difficulty_choices = ['easy', 'moderate', 'challenging']
            
            tour = Tour.objects.create(
                title=random.choice(tour_titles),
                description=f"Experience the beauty and culture of {location[0]}",
                guide=random.choice(created_guides),
                duration=random.choice(duration_choices),
                difficulty=random.choice(difficulty_choices),
                price=random.randint(30, 200),
                max_participants=random.randint(5, 15),
                location=f"{location[0]}, {location[1]}",
                latitude=random.uniform(35.0, 60.0),
                longitude=random.uniform(-10.0, 30.0),
                included_services="Guide service, Equipment rental, Refreshments",
                excluded_services="Transportation to meeting point, Personal expenses",
                meeting_point=f"Central location in {location[0]}",
                cancellation_policy="Free cancellation up to 24 hours before the tour"
            )

            # Add 2-4 random languages to the tour
            selected_languages = random.sample(created_languages, random.randint(2, 4))
            for lang in selected_languages:
                tour.languages.add(lang)

            # Create 3-5 future tour dates for each tour
            for _ in range(random.randint(3, 5)):
                future_date = timezone.now() + timedelta(days=random.randint(1, 60))
                hour = random.randint(9, 17)
                minute = random.choice([0, 15, 30, 45])
                
                TourDate.objects.create(
                    tour=tour,
                    start_date=future_date.date(),
                    start_time=future_date.time().replace(hour=hour, minute=minute),
                    max_spots=tour.max_participants,
                    booked_spots=0
                )

        self.stdout.write(self.style.SUCCESS('Successfully generated dummy tours')) 