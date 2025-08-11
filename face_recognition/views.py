from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
import base64
import uuid
import os
import time
from datetime import datetime
import numpy as np

from .models import FaceEncoding, FaceRecognitionLog
from authentication.models import CustomUser


class FaceEnrollmentView(LoginRequiredMixin, TemplateView):
    """Face enrollment page"""
    template_name = 'face_recognition/enrollment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['existing_encodings'] = FaceEncoding.objects.filter(
            user=self.request.user,
            is_active=True
        ).count()
        context['enrollment_session_id'] = str(uuid.uuid4())
        return context


class FaceRecognitionView(LoginRequiredMixin, TemplateView):
    """Face recognition page"""
    template_name = 'face_recognition/recognition.html'


class FaceEncodingListView(LoginRequiredMixin, ListView):
    """List user's face encodings"""
    model = FaceEncoding
    template_name = 'face_recognition/encoding_list.html'
    context_object_name = 'encodings'
    paginate_by = 10

    def get_queryset(self):
        return FaceEncoding.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-is_primary', '-created_at')


@method_decorator(csrf_exempt, name='dispatch')
class EnrollFaceAPIView(APIView):
    """API for face enrollment"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            images = data.get('images', [])

            if not images:
                return JsonResponse({
                    'success': False,
                    'error': 'No images provided'
                }, status=400)

            # Simulate face processing
            processed_encodings = []
            for i, image_data in enumerate(images):
                # In real implementation, this would use face_recognition library
                # For now, we'll simulate the process

                # Simulate face detection and encoding
                time.sleep(0.5)  # Simulate processing time

                # Create mock encoding (in real app, this would be actual face encoding)
                mock_encoding = np.random.rand(128).tolist()
                confidence = 0.85 + (np.random.rand() * 0.15)  # Random confidence 0.85-1.0

                # Save encoding to database
                face_encoding = FaceEncoding.objects.create(
                    user=request.user,
                    encoding_data=json.dumps(mock_encoding),
                    confidence_score=confidence,
                    source='enrollment',
                    is_primary=(i == 0),  # First encoding is primary
                    image_quality_score=0.9
                )

                processed_encodings.append({
                    'id': str(face_encoding.id),
                    'confidence': confidence,
                    'quality': 0.9
                })

            # Update user's face enrollment status
            request.user.is_face_enrolled = True
            request.user.save()

            return JsonResponse({
                'success': True,
                'message': f'Successfully enrolled {len(processed_encodings)} face encodings',
                'encodings': processed_encodings
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class RecognizeImageAPIView(APIView):
    """API for face recognition"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            image_data = data.get('image')

            if not image_data:
                return JsonResponse({
                    'success': False,
                    'error': 'No image provided'
                }, status=400)

            # Simulate face recognition process
            time.sleep(1)  # Simulate processing time

            # In real implementation, this would:
            # 1. Decode the image
            # 2. Detect faces in the image
            # 3. Extract face encodings
            # 4. Compare with stored encodings
            # 5. Return the best match

            # For simulation, we'll assume recognition is successful for enrolled users
            if request.user.is_face_enrolled:
                confidence = 0.92

                # Log the recognition attempt
                recognition_log = FaceRecognitionLog.objects.create(
                    user=request.user,
                    result='success',
                    confidence_score=confidence,
                    face_count=1,
                    processing_time=1.0,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )

                return JsonResponse({
                    'success': True,
                    'recognized': True,
                    'user': {
                        'id': request.user.id,
                        'name': request.user.get_full_name(),
                        'employee_id': request.user.employee_id
                    },
                    'confidence': confidence,
                    'message': 'Face recognized successfully'
                })
            else:
                # User not enrolled
                FaceRecognitionLog.objects.create(
                    user=request.user,
                    result='unknown',
                    confidence_score=0.0,
                    face_count=1,
                    processing_time=1.0,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    notes='User not enrolled in face recognition system'
                )

                return JsonResponse({
                    'success': False,
                    'recognized': False,
                    'message': 'Face not recognized. Please enroll first.'
                })

        except Exception as e:
            # Log failed recognition
            FaceRecognitionLog.objects.create(
                user=None,
                result='failed',
                confidence_score=0.0,
                face_count=0,
                processing_time=0.0,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                notes=str(e)
            )

            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@login_required
@require_http_methods(["DELETE"])
def delete_face_encoding(request, encoding_id):
    """Delete a face encoding"""
    try:
        encoding = get_object_or_404(
            FaceEncoding,
            id=encoding_id,
            user=request.user
        )

        # Don't allow deletion if it's the only encoding
        user_encodings_count = FaceEncoding.objects.filter(
            user=request.user,
            is_active=True
        ).count()

        if user_encodings_count <= 1:
            return JsonResponse({
                'success': False,
                'error': 'Cannot delete the only face encoding'
            }, status=400)

        encoding.is_active = False
        encoding.save()

        # If this was the primary encoding, make another one primary
        if encoding.is_primary:
            next_encoding = FaceEncoding.objects.filter(
                user=request.user,
                is_active=True
            ).exclude(id=encoding_id).first()

            if next_encoding:
                next_encoding.is_primary = True
                next_encoding.save()

        return JsonResponse({
            'success': True,
            'message': 'Face encoding deleted successfully'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def face_recognition_stats(request):
    """Get face recognition statistics"""
    try:
        # Get user's face encodings
        encodings = FaceEncoding.objects.filter(
            user=request.user,
            is_active=True
        )

        # Get recognition logs
        recent_logs = FaceRecognitionLog.objects.filter(
            user=request.user
        )[:10]

        # Calculate stats
        total_recognitions = recent_logs.count()
        successful_recognitions = recent_logs.filter(result='success').count()
        success_rate = (successful_recognitions / total_recognitions * 100) if total_recognitions > 0 else 0

        return JsonResponse({
            'success': True,
            'stats': {
                'total_encodings': encodings.count(),
                'primary_encoding': encodings.filter(is_primary=True).first().id if encodings.filter(is_primary=True).exists() else None,
                'total_recognitions': total_recognitions,
                'successful_recognitions': successful_recognitions,
                'success_rate': round(success_rate, 2),
                'last_recognition': recent_logs.first().timestamp.isoformat() if recent_logs.exists() else None
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Legacy view classes for backward compatibility
class FaceEnrollmentCaptureView(LoginRequiredMixin, TemplateView):
    template_name = 'face_recognition/enrollment.html'

class ProcessFaceEnrollmentView(LoginRequiredMixin, TemplateView):
    template_name = 'face_recognition/enrollment.html'

class ProcessFaceRecognitionView(LoginRequiredMixin, TemplateView):
    template_name = 'face_recognition/recognition.html'

class FaceEncodingDeleteView(LoginRequiredMixin, TemplateView):
    template_name = 'face_recognition/encoding_list.html'

class CaptureImageAPIView(APIView):
    def post(self, request):
        return JsonResponse({'status': 'redirect_to_new_api'})
