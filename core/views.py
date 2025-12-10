from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models # Import models for Q objects
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

        # login(request, user)  <-- Removed automatic login
        messages.success(request, f'Account created for {username}. Please wait for admin approval.')
        return redirect('login')
    
    return render(request, 'auth/register.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_approved:
                messages.error(request, 'Your account is pending admin approval.')
                return redirect('login')
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
        return redirect('browse_events')

def landing(request):
    return render(request, 'index.html')

def browse_events(request):
    query = request.GET.get('q')
    events = Event.objects.filter(date__gte=timezone.now().date(), status='APPROVED')
    
    if query:
        events = events.filter(title__icontains=query)
        
    events = events.order_by('date', 'time')
    return render(request, 'public/home.html', {'events': events, 'query': query})

def event_detail(request, event_id):
    event = Event.objects.get(pk=event_id)
    
    # Get all booked seat locations
    bookings = Booking.objects.filter(event=event, booking_status='CONFIRMED')
    booked_seats_set = set()
    for b in bookings:
        if b.seats_booked:
            for s in b.seats_booked.split(','):
                booked_seats_set.add(s.strip())

    # Generate grid
    # Rows: 'A', 'B', 'C'... 
    # Cols: 1, 2, 3...
    
    grid_rows = []
    import string
    row_labels = list(string.ascii_uppercase) # A-Z
    
    # Handle case where rows might exceed 26 (AA, AB etc if needed, but for now simple A-Z)
    
    for r in range(event.venue_rows):
        row_char = row_labels[r] if r < 26 else f"R{r+1}"
        row_seats = []
        for c in range(1, event.venue_cols + 1):
            seat_id = f"{row_char}{c}"
            row_seats.append({
                'seat_id': seat_id,
                'row': row_char,
                'col': c,
                'is_booked': seat_id in booked_seats_set
            })
        grid_rows.append(row_seats)
    
    context = {
        'event': event,
        'grid_rows': grid_rows,
        'booked_seat_ids': list(booked_seats_set), 
    }
    return render(request, 'public/event_detail.html', context)

@login_required
@login_required
def book_ticket(request, event_id):
    if request.method == 'POST':
        from django.db import transaction
        
        event = Event.objects.get(pk=event_id)
        selected_seat_ids = request.POST.get('selected_seats') # e.g., "A1,A2"
        
        if not selected_seat_ids:
            messages.error(request, 'No seats selected.')
            return redirect('event_detail', event_id=event.id)
        
        seat_list = [s.strip() for s in selected_seat_ids.split(',')]
        quantity = len(seat_list)
        
        try:
            with transaction.atomic():
                # Lock the event row to prevent race conditions (optional but good)
                Event.objects.select_for_update().get(pk=event_id)
                
                # Check availability
                # Get all currently booked seats for this event
                existing_bookings = Booking.objects.filter(
                    event=event,
                    booking_status='CONFIRMED'
                ).select_for_update()
                
                booked_seats_set = set()
                for b in existing_bookings:
                    if b.seats_booked:
                        for s in b.seats_booked.split(','):
                            booked_seats_set.add(s.strip())
                
                # Check for overlap
                for seat in seat_list:
                    if seat in booked_seats_set:
                        raise ValueError(f'Seat {seat} is already booked.')
                
                # Create Booking
                total_cost = event.price * quantity
                Booking.objects.create(
                    event=event,
                    user=request.user,
                    total_cost=total_cost,
                    booking_status='CONFIRMED',
                    seats_booked=selected_seat_ids
                )
                
            messages.success(request, f'Booking confirmed! {quantity} tickets.')
            return redirect('my_tickets')
            
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('event_detail', event_id=event.id)
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('event_detail', event_id=event.id)
    
    return redirect('browse_events')

@login_required
def my_tickets(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'public/my_tickets.html', {'bookings': bookings})


@login_required
def admin_dashboard(request):
    if request.user.role != 'ADMIN':
        return redirect('browse_events')
    
    total_users = User.objects.count()
    active_events = Event.objects.filter(status='APPROVED').count()
    total_bookings = Booking.objects.count()
    pending_users_count = User.objects.filter(is_approved=False).count()
    pending_events_count = Event.objects.filter(status='PENDING').count()
    
    context = {
        'total_users': total_users,
        'active_events': active_events,
        'total_bookings': total_bookings,
        'pending_users_count': pending_users_count,
        'pending_events_count': pending_events_count,
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def user_list(request):
    if request.user.role != 'ADMIN':
        return redirect('browse_events')
    
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin/user_list.html', {'users': users})

@login_required
def host_list(request):
    if request.user.role != 'ADMIN':
        return redirect('browse_events')
    
    hosts = User.objects.filter(role='HOST').order_by('-date_joined')
    return render(request, 'admin/host_list.html', {'hosts': hosts})

@login_required
def pending_users(request):
    if request.user.role != 'ADMIN':
        return redirect('browse_events')
    
    users = User.objects.filter(is_approved=False).order_by('date_joined')
    return render(request, 'admin/pending_users.html', {'users': users})

@login_required
def approve_user(request, user_id):
    if request.user.role != 'ADMIN':
        return redirect('browse_events')
    
    user = User.objects.get(pk=user_id)
    user.is_approved = True
    user.save()
    messages.success(request, f'User {user.username} approved.')
    return redirect('pending_users')

@login_required
def reject_user(request, user_id):
    if request.user.role != 'ADMIN':
        return redirect('browse_events')
    
    user = User.objects.get(pk=user_id)
    user.delete()
    messages.success(request, f'User {user.username} rejected and removed.')
    return redirect('pending_users')

@login_required
def admin_pending_events(request):
    if request.user.role != 'ADMIN':
        return redirect('browse_events')
    
    events = Event.objects.filter(status='PENDING').order_by('date')
    return render(request, 'admin/pending_events.html', {'events': events})

@login_required
def approve_event(request, event_id):
    if request.user.role != 'ADMIN':
        return redirect('browse_events')
    
    event = Event.objects.get(pk=event_id)
    event.status = 'APPROVED'
    event.save()
    messages.success(request, f'Event "{event.title}" approved.')
    return redirect('admin_pending_events')

@login_required
def reject_event(request, event_id):
    if request.user.role != 'ADMIN':
        return redirect('browse_events')
    
    event = Event.objects.get(pk=event_id)
    event.delete()
    messages.success(request, f'Event "{event.title}" rejected.')
    return redirect('admin_pending_events')

@login_required
def admin_event_list(request):
    if request.user.role != 'ADMIN':
        return redirect('browse_events')
    
    from django.db.models import Sum, Count
    
    events = Event.objects.annotate(
        revenue=Sum('bookings__total_cost', default=0),
        confirmed_bookings_count=Count('bookings', filter=models.Q(bookings__booking_status='CONFIRMED'))
    ).order_by('-date', '-time')
    
    event_stats = []
    for event in events:
        # Calculate booked seats count by parsing CSV strings
        bookings = Booking.objects.filter(event=event, booking_status='CONFIRMED')
        booked_count = 0
        for b in bookings:
            if b.seats_booked:
                booked_count += len(b.seats_booked.split(','))
        
        total_capacity = event.venue_rows * event.venue_cols
        balance_seats = total_capacity - booked_count
        
        event_stats.append({
            'event': event,
            'revenue': event.revenue,
            'total_capacity': total_capacity,
            'balance_seats': balance_seats,
            'booked_count': booked_count
        })
        
    return render(request, 'admin/event_list.html', {'event_stats': event_stats})

@login_required
def host_dashboard(request):
    if request.user.role != 'HOST':
        return redirect('browse_events')
    
    # Events where the user is the host
    events = Event.objects.filter(host=request.user)
    return render(request, 'host/dashboard.html', {'events': events})

@login_required
def create_event(request):
    if request.user.role != 'HOST':
        return redirect('browse_events')
    
    if not request.user.is_approved:
        messages.error(request, 'You are not approved to create events yet.')
        return redirect('host_dashboard')

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.host = request.user  # Assign the current user as host
            event.save()
            messages.success(request, 'Event created! It is pending admin approval.')
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
    
    booked_seats_set = set()
    for b in bookings:
        if b.seats_booked:
            for s in b.seats_booked.split(','):
                booked_seats_set.add(s.strip())
                
    seats_sold_count = len(booked_seats_set)
    total_capacity = event.venue_rows * event.venue_cols
    balance_seats = total_capacity - seats_sold_count
    
    # Generate grid
    import string
    row_labels = list(string.ascii_uppercase)
    
    grid_rows = []
    for r in range(event.venue_rows):
        row_char = row_labels[r] if r < 26 else f"R{r+1}"
        row_seats = []
        for c in range(1, event.venue_cols + 1):
            seat_id = f"{row_char}{c}"
            row_seats.append({
                'seat_id': seat_id,
                'row': row_char,
                'col': c,
                'is_booked': seat_id in booked_seats_set
            })
        grid_rows.append(row_seats)

    context = {
        'event': event,
        'total_revenue': total_revenue,
        'seats_sold_count': seats_sold_count,
        'balance_seats': balance_seats,
        'total_capacity': total_capacity,
        'grid_rows': grid_rows,
    }
    return render(request, 'host/event_detail.html', context)


@login_required
def delete_event(request, event_id):
    if request.user.role != 'ADMIN':
        messages.error(request, 'Unauthorized action.')
        return redirect('browse_events')
    
    event = Event.objects.get(pk=event_id)
    event.delete()
    messages.success(request, f'Event "{event.title}" has been deleted.')
    return redirect('admin_event_list')
