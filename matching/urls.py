from django.urls import path
from . import views

urlpatterns = [
    path('', views.matches, name='matches'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('notifications/clear-all/', views.clear_all_notifications, name='clear_all_notifications'),
    path('delete-match/<int:listing_id>/', views.delete_match, name='delete_match'),
    
    # API endpoints for AJAX
    path('api/unread-count/', views.unread_notifications_count, name='unread_notifications_count'),
    path('api/notifications/', views.notifications_api, name='notifications_api'),
]