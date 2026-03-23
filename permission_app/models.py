from django.db import models
from users.models import CustomUser
from internship_app.models import Internship


class PermissionRequest(models.Model):

    STATUS_CHOICES = [
        ('pending_faculty', 'Pending Faculty'),
        ('pending_hod', 'Pending HOD'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='permission_requests_permission_app'
    )

    internship = models.ForeignKey(Internship, on_delete=models.CASCADE)

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending_faculty'
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    offer_letter = models.FileField(
        upload_to='offer_letters/',
        null=True,
        blank=True
    )

    completion_certificate = models.FileField(
        upload_to='certificates/',
        null=True,
        blank=True
    )

    feedback = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.email} - {self.internship.title}"