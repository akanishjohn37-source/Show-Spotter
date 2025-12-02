from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrator'),
        ('HOST', 'Host'),
        ('PUBLIC', 'Public User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='PUBLIC')
    is_approved = models.BooleanField(default=True) # False for Host initially

    def save(self, *args, **kwargs):
        if self.role == 'HOST' and not self.pk:
            self.is_approved = False
        super().save(*args, **kwargs)

class Event(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    venue_rows = models.IntegerField()
    venue_cols = models.IntegerField()
    
    @property
    def total_capacity(self):
        return self.venue_rows * self.venue_cols

    def __str__(self):
        return self.title

class Booking(models.Model):
    STATUS_CHOICES = (
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    seats_booked = models.TextField() # Comma-separated list of seat IDs e.g. "A1,A2"
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    booking_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='CONFIRMED')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
