from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings  # custom user

# ----------------- INTERNSHIP MODEL -----------------
class Internship(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='internships_posted'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')
    deadline = models.DateField()
    duration = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100, blank=True)
    company_name = models.CharField(max_length=150, blank=True)
    domain = models.CharField(max_length=100, blank=True)
    internship_mode = models.CharField(
        max_length=20,
        choices=(
            ("online", "Online"),
            ("offline", "Offline"),
            ("hybrid", "Hybrid"),
        ),
        blank=True,
        null=True,
    )
    stipend_type = models.CharField(
        max_length=20,
        choices=(
            ("paid", "Paid"),
            ("unpaid", "Unpaid"),
        ),
        blank=True,
        null=True,
    )
    stipend_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# ----------------- APPLICATION MODEL -----------------
class Application(models.Model):
    STATUS_CHOICES = (
    ('applied', 'Applied'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('rejected', 'Rejected'),
)

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    internship = models.ForeignKey(
        Internship,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.FileField(upload_to='cover_letters/', blank=True, null=True)
    company_name_snapshot = models.CharField(max_length=150, blank=True)
    domain_snapshot = models.CharField(max_length=100, blank=True)
    internship_mode_snapshot = models.CharField(
        max_length=20,
        choices=(
            ("online", "Online"),
            ("offline", "Offline"),
            ("hybrid", "Hybrid"),
        ),
        blank=True,
        null=True,
    )
    stipend_type_snapshot = models.CharField(
        max_length=20,
        choices=(
            ("paid", "Paid"),
            ("unpaid", "Unpaid"),
        ),
        blank=True,
        null=True,
    )
    stipend_amount_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    start_date_snapshot = models.DateField(blank=True, null=True)
    end_date_snapshot = models.DateField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        student_name = f"{self.student.first_name} {self.student.last_name}" if self.student else "Unknown"
        return f"{student_name} - {self.internship.title}"