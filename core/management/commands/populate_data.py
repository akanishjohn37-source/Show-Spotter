from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import User, Auditorium, Seat, Event
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populate database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating data...')

        # Create Users
        admin_user, created = User.objects.get_or_create(username='admin', email='admin@example.com')
        if created:
            admin_user.set_password('admin123')
            admin_user.role = 'ADMIN'
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write('Created Admin user')

        host_user, created = User.objects.get_or_create(username='host1', email='host1@example.com')
        if created:
            host_user.set_password('host123')
            host_user.role = 'HOST'
            host_user.is_approved = True
            host_user.save()
            self.stdout.write('Created Host user')

        public_user, created = User.objects.get_or_create(username='user1', email='user1@example.com')
        if created:
            public_user.set_password('user123')
            public_user.role = 'PUBLIC'
            public_user.save()
            self.stdout.write('Created Public user')

        # Create Event
        import datetime
        event_date = timezone.now().date() + datetime.timedelta(days=1)
        event_time = datetime.time(19, 0) # 7 PM
        
        event, created = Event.objects.get_or_create(
            title='Rock Concert',
            host=host_user,
            defaults={
                'description': 'A live rock concert featuring top bands.',
                'date': event_date,
                'time': event_time,
                'price': 50.00,
                'venue_rows': 5,
                'venue_cols': 10,
                'location_lat': 40.7128,
                'location_lng': -74.0060,
                'status': 'APPROVED',
                'image_url': 'https://via.placeholder.com/800x400'
            }
        )
        if created:
            self.stdout.write(f'Created Event: {event.title}')

        self.stdout.write(self.style.SUCCESS('Data population complete!'))
