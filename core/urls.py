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
    path('admin/hosts/', views.host_list, name='host_list'),
    path('admin/approve/<int:user_id>/', views.approve_host, name='approve_host'),
    path('admin/reject/<int:user_id>/', views.reject_host, name='reject_host'),
    path('host-dashboard/', views.host_dashboard, name='host_dashboard'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/book/', views.book_ticket, name='book_ticket'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('create-event/', views.create_event, name='create_event'),
]
