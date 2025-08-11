from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
import uuid


class Department(models.Model):
    """Department model for organizing users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    """Extended User model with additional fields for face recognition system"""

    USER_ROLES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
        ('security', 'Security Personnel'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator(r'^[A-Z0-9]+$', 'Employee ID must contain only uppercase letters and numbers')]
    )
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='employee')
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.')]
    )
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)

    # Face recognition related fields
    is_face_enrolled = models.BooleanField(default=False)
    face_enrollment_date = models.DateTimeField(blank=True, null=True)

    # Account status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_attendance = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['employee_id']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.employee_id} - {self.get_full_name()}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    @property
    def has_face_encodings(self):
        """Check if user has any face encodings"""
        return self.face_encodings.filter(is_active=True).exists()

    @property
    def active_face_encodings_count(self):
        """Get count of active face encodings"""
        return self.face_encodings.filter(is_active=True).count()
