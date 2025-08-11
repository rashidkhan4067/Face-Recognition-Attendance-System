from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
from datetime import datetime, time


class AttendanceRecord(models.Model):
    """Main attendance record model"""

    ATTENDANCE_TYPES = [
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
        ('break_start', 'Break Start'),
        ('break_end', 'Break End'),
    ]

    RECOGNITION_METHODS = [
        ('face', 'Face Recognition'),
        ('manual', 'Manual Entry'),
        ('card', 'ID Card'),
        ('mobile', 'Mobile App'),
    ]

    STATUS_CHOICES = [
        ('present', 'Present'),
        ('late', 'Late'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
        ('on_leave', 'On Leave'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)

    # Time tracking
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    break_start_time = models.DateTimeField(null=True, blank=True)
    break_end_time = models.DateTimeField(null=True, blank=True)

    # Calculated fields
    total_hours = models.DurationField(null=True, blank=True)
    break_duration = models.DurationField(null=True, blank=True)
    overtime_hours = models.DurationField(null=True, blank=True)

    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    recognition_method = models.CharField(max_length=20, choices=RECOGNITION_METHODS, default='face')

    # Face recognition specific
    recognition_confidence = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    face_encoding_used = models.UUIDField(null=True, blank=True)

    # Location and device info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_info = models.TextField(blank=True)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Administrative
    is_approved = models.BooleanField(default=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_attendance_records'
    )
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-check_in_time']
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date', 'status']),
            models.Index(fields=['recognition_method']),
        ]

    def __str__(self):
        return f"{self.user.employee_id} - {self.date} - {self.status}"

    @property
    def is_late(self):
        """Check if the employee was late"""
        if self.check_in_time:
            # Assuming standard work start time is 9:00 AM
            standard_start = time(9, 0)
            return self.check_in_time.time() > standard_start
        return False

    @property
    def worked_hours(self):
        """Calculate total worked hours"""
        if self.check_in_time and self.check_out_time:
            total_time = self.check_out_time - self.check_in_time
            if self.break_duration:
                total_time -= self.break_duration
            return total_time
        return None

    def calculate_break_duration(self):
        """Calculate break duration"""
        if self.break_start_time and self.break_end_time:
            return self.break_end_time - self.break_start_time
        return None

    def save(self, *args, **kwargs):
        # Auto-calculate break duration
        if self.break_start_time and self.break_end_time:
            self.break_duration = self.calculate_break_duration()

        # Auto-calculate total hours
        if self.check_in_time and self.check_out_time:
            self.total_hours = self.worked_hours

        # Determine status based on timing
        if self.check_in_time and self.is_late:
            self.status = 'late'
        elif self.check_in_time:
            self.status = 'present'

        super().save(*args, **kwargs)


class AttendanceSettings(models.Model):
    """Global attendance settings"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Work schedule
    standard_work_start = models.TimeField(default=time(9, 0))
    standard_work_end = models.TimeField(default=time(17, 0))
    late_threshold_minutes = models.IntegerField(default=15)

    # Break settings
    standard_break_duration = models.DurationField(default=timezone.timedelta(hours=1))
    max_break_duration = models.DurationField(default=timezone.timedelta(hours=2))

    # Overtime settings
    overtime_threshold_hours = models.FloatField(default=8.0)
    overtime_rate_multiplier = models.FloatField(default=1.5)

    # Face recognition settings
    min_recognition_confidence = models.FloatField(default=0.6)
    allow_manual_override = models.BooleanField(default=True)
    require_admin_approval = models.BooleanField(default=False)

    # Notification settings
    send_late_notifications = models.BooleanField(default=True)
    send_absence_notifications = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Attendance Settings'
        verbose_name_plural = 'Attendance Settings'

    def __str__(self):
        return f"Attendance Settings - {self.created_at.date()}"

    @classmethod
    def get_current_settings(cls):
        """Get the current active settings"""
        return cls.objects.filter(is_active=True).first()


class LeaveRequest(models.Model):
    """Leave request model"""

    LEAVE_TYPES = [
        ('sick', 'Sick Leave'),
        ('vacation', 'Vacation'),
        ('personal', 'Personal Leave'),
        ('emergency', 'Emergency Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)

    # Date range
    start_date = models.DateField()
    end_date = models.DateField()
    is_half_day = models.BooleanField(default=False)

    # Request details
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Approval workflow
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_leave_requests'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.user.employee_id} - {self.leave_type} - {self.start_date} to {self.end_date}"

    @property
    def duration_days(self):
        """Calculate leave duration in days"""
        if self.is_half_day:
            return 0.5
        return (self.end_date - self.start_date).days + 1

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date")
