from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('admin/', admin.site.urls),

    # Users (login/register/dashboard)
    path('', include('users.urls')),

    # Internship system
    path('internships/', include('internship_app.urls')),

    # Permissions
    path('permissions/', include('permission_app.urls')),

    # Notifications
    path('notifications/', include('notification_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)