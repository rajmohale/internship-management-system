from django.contrib import admin
from .models import Internship, Application
from django.utils.html import format_html

@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ('title', 'faculty', 'status', 'deadline', 'duration', 'location', 'created_at', 'updated_at')
    list_filter = ('status', 'faculty',)
    search_fields = ('title', 'description', 'faculty__first_name', 'faculty__last_name')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'internship', 'status', 'applied_at', 'updated_at', 'resume_link', 'cover_letter_link')
    list_filter = ('status', 'internship',)
    search_fields = ('student__email', 'internship__title',)
    readonly_fields = ('applied_at', 'updated_at')

    fieldsets = (
        ('Application Info', {'fields': ('student', 'internship', 'status')}),
        ('Documents', {'fields': ('resume', 'cover_letter', 'additional_notes', 'offer_letter', 'completion_certificate')}),
        ('Timestamps', {'fields': ('applied_at', 'updated_at')}),
        ('Feedback', {'fields': ('feedback',)}),
    )

    # Optional: clickable download links
    def resume_link(self, obj):
        if obj.resume:
            return format_html(f'<a href="{obj.resume.url}" target="_blank">Download</a>')
        return "-"
    resume_link.short_description = 'Resume'

    def cover_letter_link(self, obj):
        if obj.cover_letter:
            return format_html(f'<a href="{obj.cover_letter.url}" target="_blank">Download</a>')
        return "-"
    cover_letter_link.short_description = 'Cover Letter'