from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


# ---------------- USER MANAGER ----------------
class MyAccountManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, first_name, last_name, password=None):

        user = self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )

        user.role = 'admin'
        user.status = 'active'
        user.is_staff = True
        user.is_superuser = True
        user.is_admin = True
        user.is_active = True

        user.save(using=self._db)

        return user


# ---------------- CUSTOM USER MODEL ----------------
class CustomUser(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('hod', 'HOD'),
        ('admin', 'Admin'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('rejected', 'Rejected'),
    )

    # Basic Info
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    approval_stage = models.CharField(
        max_length=20,
        default='faculty'
    )

    # Permissions
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    # Dates
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)

    # Profile fields
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # ---------------- STUDENT FIELDS ----------------
    STUDENT_CLASS_CHOICES = (
        ('ce1', 'CE1'),
        ('ce2', 'CE2'),
        ('it1', 'IT1'),
        ('it2', 'IT2'),
        ('aids', 'AIDS'),
        ('aids2', 'AIDS2'),
        ('ele1', 'ELE1'),
        ('ele2', 'ELE2'),
        ('mech1', 'MECH1'),
        ('mech2', 'MECH2'),
        ('entc1', 'ENTC1'),
        ('entc2', 'ENTC2'),
    )
    student_class = models.CharField(max_length=10, choices=STUDENT_CLASS_CHOICES, blank=True, null=True)
    branch = models.CharField(max_length=50, blank=True, null=True)
    year = models.CharField(max_length=10, blank=True, null=True)
    prn = models.CharField(max_length=20, blank=True, null=True)
    college_id_photo = models.ImageField(upload_to='college_ids/', blank=True, null=True)
    skills = models.TextField(blank=True, null=True)

    # ---------------- FACULTY FIELDS ----------------
    department = models.CharField(max_length=50, blank=True, null=True)
    specification = models.CharField(max_length=50, blank=True, null=True)
    designation = models.CharField(max_length=50, blank=True, null=True)

    # ---------------- ADMIN FIELD ----------------
    admin_department = models.CharField(max_length=50, blank=True, null=True)

    # Manager
    objects = MyAccountManager()

    # Authentication settings
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.email} ({self.role})"