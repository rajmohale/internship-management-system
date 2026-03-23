from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import CustomUser
from notification_app.models import Notification


# ---------- ADMIN ACTIONS ----------

def approve_students(modeladmin, request, queryset):
    queryset.update(status='active', is_active=True)

    for user in queryset:
        Notification.objects.create(
            user=user,
            message="Your student account has been approved."
        )

approve_students.short_description = "Approve selected students"


def reject_students(modeladmin, request, queryset):
    queryset.update(status='rejected', is_active=False)

    for user in queryset:
        Notification.objects.create(
            user=user,
            message="Your student account has been rejected."
        )

reject_students.short_description = "Reject selected students"


def approve_faculty(modeladmin, request, queryset):
    queryset.update(status='active', is_active=True)

    for user in queryset:
        Notification.objects.create(
            user=user,
            message="Your faculty account has been approved."
        )

approve_faculty.short_description = "Approve selected faculty"


def reject_faculty(modeladmin, request, queryset):
    queryset.update(status='rejected', is_active=False)

    for user in queryset:
        Notification.objects.create(
            user=user,
            message="Your faculty account has been rejected."
        )

reject_faculty.short_description = "Reject selected faculty"


# ---------- CUSTOM USER ADMIN ----------

class CustomUserAdmin(UserAdmin):

    model = CustomUser

    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "status",
        "is_active",
        "date_joined",
        "profile_pic_thumb",
    )

    # ❌ removed gender
    list_filter = ("role", "status")

    search_fields = ("email", "first_name", "last_name", "prn")

    ordering = ("-date_joined",)

    # ❌ removed last_logout
    readonly_fields = ("date_joined", "last_login")

    actions = [
        approve_students,
        reject_students,
        approve_faculty,
        reject_faculty,
    ]

    fieldsets = (
        (None, {"fields": ("email", "password")}),

        ("Personal Info", {
            "fields": ("first_name", "last_name", "phone_number", "profile_picture")
        }),

        ("Academic Info", {
            "fields": ("role", "status", "branch", "year", "prn")
        }),

        ("Faculty Info", {
            "fields": ("department", "specification", "designation")
        }),

        ("Admin Info", {
            "fields": ("admin_department",)
        }),

        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions"
            )
        }),

        ("Important Dates", {
            "fields": ("last_login", "date_joined")
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "password1",
                "password2",
                "role",
                "status",
                "is_active",
                "is_staff",
            ),
        }),
    )

    def profile_pic_thumb(self, obj):
        if obj.profile_picture and hasattr(obj.profile_picture, "url"):
            return format_html(
                '<img src="{}" width="40" style="border-radius:50%;" />',
                obj.profile_picture.url
            )
        return "-"

    profile_pic_thumb.short_description = "Profile"


admin.site.register(CustomUser, CustomUserAdmin)