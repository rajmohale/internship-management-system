from django.contrib import admin
from .models import PermissionRequest

class PermissionRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'internship', 'status', 'submitted_at')  # use submitted_at
    list_filter = ('status',)
    search_fields = ('student__email', 'internship__title')

admin.site.register(PermissionRequest, PermissionRequestAdmin)