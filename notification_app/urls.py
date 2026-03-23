from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_list, name='notifications_list'),
    path('read/<int:notification_id>/', views.mark_read, name='mark_notification_read'),
    path('review/<int:permission_id>/', views.review_permission, name='review_permission'),
]