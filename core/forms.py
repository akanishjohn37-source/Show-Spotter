from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'time', 'price', 'venue_rows', 'venue_cols', 'image_url', 'location_lat', 'location_lng']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'location_lat': forms.HiddenInput(),
            'location_lng': forms.HiddenInput(),
        }
