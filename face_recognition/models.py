from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import json
import numpy as np


class FaceEncoding(models.Model):
    """Store face encodings for users"""

    ENCODING_SOURCES = [
        ('enrollment', 'Initial Enrollment'),
        ('update', 'Profile Update'),
        ('retrain', 'Model Retrain'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='face_encodings')
    encoding_data = models.TextField(help_text="JSON serialized face encoding array")
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Confidence score of the face encoding"
    )
    source = models.CharField(max_length=20, choices=ENCODING_SOURCES, default='enrollment')
    image_path = models.CharField(max_length=500, blank=True, help_text="Path to the source image")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False, help_text="Primary encoding for recognition")

    # Face detection metadata
    face_location = models.TextField(blank=True, help_text="JSON serialized face location coordinates")
    image_quality_score = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )

    class Meta:
        ordering = ['-is_primary', '-confidence_score', '-created_at']
        verbose_name = 'Face Encoding'
        verbose_name_plural = 'Face Encodings'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['is_primary', 'is_active']),
        ]

    def __str__(self):
        return f"Face Encoding for {self.user.employee_id} - {self.confidence_score:.2f}"

    def set_encoding(self, encoding_array):
        """Set face encoding from numpy array"""
        if isinstance(encoding_array, np.ndarray):
            self.encoding_data = json.dumps(encoding_array.tolist())
        else:
            self.encoding_data = json.dumps(encoding_array)

    def get_encoding(self):
        """Get face encoding as numpy array"""
        if self.encoding_data:
            return np.array(json.loads(self.encoding_data))
        return None

    def set_face_location(self, location):
        """Set face location coordinates"""
        if location:
            self.face_location = json.dumps(location)

    def get_face_location(self):
        """Get face location coordinates"""
        if self.face_location:
            return json.loads(self.face_location)
        return None

    def save(self, *args, **kwargs):
        # Ensure only one primary encoding per user
        if self.is_primary:
            FaceEncoding.objects.filter(
                user=self.user,
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)


class FaceRecognitionLog(models.Model):
    """Log all face recognition attempts"""

    RECOGNITION_RESULTS = [
        ('success', 'Successful Recognition'),
        ('failed', 'Failed Recognition'),
        ('multiple', 'Multiple Faces Detected'),
        ('no_face', 'No Face Detected'),
        ('low_quality', 'Low Quality Image'),
        ('unknown', 'Unknown Person'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='recognition_logs'
    )
    result = models.CharField(max_length=20, choices=RECOGNITION_RESULTS)
    confidence_score = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )

    # Image data
    image_path = models.CharField(max_length=500, blank=True)
    image_hash = models.CharField(max_length=64, blank=True, help_text="SHA256 hash of the image")

    # Recognition metadata
    processing_time = models.FloatField(null=True, blank=True, help_text="Processing time in seconds")
    face_count = models.IntegerField(default=0)
    matched_encoding_id = models.UUIDField(null=True, blank=True)

    # System metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Additional context
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Face Recognition Log'
        verbose_name_plural = 'Face Recognition Logs'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['result', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        user_info = f"{self.user.employee_id}" if self.user else "Unknown"
        return f"Recognition Log - {user_info} - {self.result} - {self.timestamp}"
