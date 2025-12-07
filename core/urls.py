from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_dispatch, name='dashboard_dispatch'),
    
    # Placeholders
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/hosts/', views.host_list, name='host_list'),
    path('manage/events/', views.admin_event_list, name='admin_event_list'),
    path('manage/events/pending/', views.admin_pending_events, name='admin_pending_events'),
    path('manage/events/<int:event_id>/approve/', views.approve_event, name='approve_event'),
    path('manage/events/<int:event_id>/reject/', views.reject_event, name='reject_event'),
    path('manage/events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('manage/approve/<int:user_id>/', views.approve_host, name='approve_host'),
    path('manage/reject/<int:user_id>/', views.reject_host, name='reject_host'),
    path('host-dashboard/', views.host_dashboard, name='host_dashboard'),
    path('host/event/<int:event_id>/', views.host_event_detail, name='host_event_detail'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/book/', views.book_ticket, name='book_ticket'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('create-event/', views.create_event, name='create_event'),
]
