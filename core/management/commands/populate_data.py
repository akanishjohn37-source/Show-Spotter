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

        # Create Auditorium
        auditorium, created = Auditorium.objects.get_or_create(
            name='Main Hall',
            host=host_user,
            defaults={
                'location': 'Downtown',
                'total_rows': 5,
                'total_cols': 10
            }
        )
        if created:
            self.stdout.write(f'Created Auditorium: {auditorium.name}')
            # Create Seats
            seats = []
            for r in range(1, auditorium.total_rows + 1):
                row_letter = chr(64 + r) # A, B, C...
                for c in range(1, auditorium.total_cols + 1):
                    seats.append(Seat(auditorium=auditorium, row_letter=row_letter, col_number=c))
            Seat.objects.bulk_create(seats)
            self.stdout.write(f'Created {len(seats)} seats for {auditorium.name}')

        # Create Event
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=3)
        
        event, created = Event.objects.get_or_create(
            title='Rock Concert',
            auditorium=auditorium,
            defaults={
                'description': 'A live rock concert featuring top bands.',
                'start_time': start_time,
                'end_time': end_time,
                'price': 50.00,
                'image_url': 'https://via.placeholder.com/800x400'
            }
        )
        if created:
            self.stdout.write(f'Created Event: {event.title}')

        self.stdout.write(self.style.SUCCESS('Data population complete!'))
