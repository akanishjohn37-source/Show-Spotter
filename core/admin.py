from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Event, Booking

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_approved', 'is_staff')
    list_filter = ('role', 'is_approved', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role', 'is_approved')}),
    )

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'host', 'date', 'price', 'venue_rows', 'venue_cols')
    list_filter = ('date',)
    search_fields = ('title', 'description')

class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'user', 'total_cost', 'booking_status', 'created_at')
    list_filter = ('booking_status',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Booking, BookingAdmin)
