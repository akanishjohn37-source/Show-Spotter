from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import json
from .models import User, Event, Booking
from .forms import EventForm

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.role = role
        user.save()

        login(request, user)
        messages.success(request, f'Welcome, {username}!')
        return redirect('dashboard_dispatch')
    
    return render(request, 'auth/register.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard_dispatch')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

@login_required
def dashboard_dispatch(request):
    user = request.user
    if user.role == 'ADMIN':
        return redirect('admin_dashboard')
    elif user.role == 'HOST':
        if not user.is_approved:
            messages.warning(request, 'Your account is pending approval by an administrator.')
            logout(request)
            return redirect('login')
        return redirect('host_dashboard')
    else:
        return redirect('home')

def home(request):
    events = Event.objects.filter(date__gte=timezone.now().date()).order_by('date')
    return render(request, 'public/home.html', {'events': events})

@login_required
def event_detail(request, event_id):
    event = Event.objects.get(pk=event_id)
    
    # Get all booked seats for this event
    bookings = Booking.objects.filter(event=event, booking_status='CONFIRMED')
    booked_seats = []
    for booking in bookings:
        if booking.seats_booked:
            booked_seats.extend(booking.seats_booked.split(','))
    
    context = {
        'event': event,
        'booked_seats': json.dumps(booked_seats), # Pass as JSON for JS
        'rows': range(1, event.venue_rows + 1),
        'cols': range(1, event.venue_cols + 1),
    }
    return render(request, 'public/event_detail.html', context)

@login_required
def book_ticket(request, event_id):
    if request.method == 'POST':
        event = Event.objects.get(pk=event_id)
        selected_seats = request.POST.get('selected_seats') # e.g., "A1,A2"
        
        if not selected_seats:
            messages.error(request, 'No seats selected.')
            return redirect('event_detail', event_id=event.id)
        
        seat_list = selected_seats.split(',')
        quantity = len(seat_list)
        
        # Concurrency Check: Verify if seats are still available
        bookings = Booking.objects.filter(event=event, booking_status='CONFIRMED')
        all_booked = []
        for b in bookings:
            if b.seats_booked:
                all_booked.extend(b.seats_booked.split(','))
        
        for seat in seat_list:
            if seat in all_booked:
                messages.error(request, f'Seat {seat} was just booked by someone else. Please try again.')
                return redirect('event_detail', event_id=event.id)
        
        # Create Booking
        total_cost = event.price * quantity
        Booking.objects.create(
            event=event,
            user=request.user,
            seats_booked=selected_seats,
            total_cost=total_cost,
            booking_status='CONFIRMED'
        )
        
        messages.success(request, f'Booking confirmed! Tickets: {selected_seats}')
        return redirect('my_tickets')
    
    return redirect('home')

@login_required
def my_tickets(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'public/my_tickets.html', {'bookings': bookings})


@login_required
def admin_dashboard(request):
    if request.user.role != 'ADMIN':
        return redirect('home')
    
    total_users = User.objects.count()
    active_events = Event.objects.count()
    total_bookings = Booking.objects.count()
    pending_hosts = User.objects.filter(role='HOST', is_approved=False).count()
    
    context = {
        'total_users': total_users,
        'active_events': active_events,
        'total_bookings': total_bookings,
        'pending_hosts': pending_hosts,
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def host_list(request):
    if request.user.role != 'ADMIN':
        return redirect('home')
    
    hosts = User.objects.filter(role='HOST', is_approved=False)
    return render(request, 'admin/host_list.html', {'hosts': hosts})

@login_required
def approve_host(request, user_id):
    if request.user.role != 'ADMIN':
        return redirect('home')
    
    user = User.objects.get(pk=user_id)
    user.is_approved = True
    user.save()
    messages.success(request, f'Host {user.username} approved.')
    return redirect('host_list')

@login_required
def reject_host(request, user_id):
    if request.user.role != 'ADMIN':
        return redirect('home')
    
    user = User.objects.get(pk=user_id)
    user.delete()
    messages.success(request, f'Host {user.username} rejected and removed.')
    return redirect('host_list')

@login_required
def admin_event_list(request):
    if request.user.role != 'ADMIN':
        return redirect('home')
    
    events = Event.objects.all().order_by('-date')
    event_stats = []
    
    for event in events:
        bookings = Booking.objects.filter(event=event, booking_status='CONFIRMED')
        revenue = sum(b.total_cost for b in bookings)
        
        booked_count = 0
        for b in bookings:
            if b.seats_booked:
                booked_count += len(b.seats_booked.split(','))
        
        total_capacity = event.venue_rows * event.venue_cols
        balance_seats = total_capacity - booked_count
        
        event_stats.append({
            'event': event,
            'revenue': revenue,
            'total_capacity': total_capacity,
            'balance_seats': balance_seats,
            'booked_count': booked_count
        })
        
    return render(request, 'admin/event_list.html', {'event_stats': event_stats})

@login_required
def host_dashboard(request):
    if request.user.role != 'HOST':
        return redirect('home')
    
    events = Event.objects.filter(host=request.user)
    return render(request, 'host/dashboard.html', {'events': events})

@login_required
def create_event(request):
    if request.user.role != 'HOST':
        return redirect('home')
    
    if not request.user.is_approved:
        messages.error(request, 'You are not approved to create events yet.')
        return redirect('host_dashboard')

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.host = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('host_dashboard')
    else:
        form = EventForm()
    
    return render(request, 'host/create_event.html', {'form': form})

@login_required
def host_event_detail(request, event_id):
    event = Event.objects.get(pk=event_id)
    if event.host != request.user:
        messages.error(request, "You are not authorized to view this event.")
        return redirect('host_dashboard')

    bookings = Booking.objects.filter(event=event, booking_status='CONFIRMED')
    
    total_revenue = sum(b.total_cost for b in bookings)
    
    booked_seats = []
    for b in bookings:
        if b.seats_booked:
            booked_seats.extend(b.seats_booked.split(','))
            
    seats_sold_count = len(booked_seats)
    total_capacity = event.venue_rows * event.venue_cols
    balance_seats = total_capacity - seats_sold_count
    
    context = {
        'event': event,
        'total_revenue': total_revenue,
        'seats_sold_count': seats_sold_count,
        'balance_seats': balance_seats,
        'total_capacity': total_capacity,
        'booked_seats': json.dumps(booked_seats),
        'rows': range(1, event.venue_rows + 1),
        'cols': range(1, event.venue_cols + 1),
    }
    return render(request, 'host/event_detail.html', context)


