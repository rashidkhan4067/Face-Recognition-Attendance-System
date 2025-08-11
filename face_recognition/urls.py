from django.urls import path
from . import views

app_name = 'face_recognition'

urlpatterns = [
    # Face enrollment
    path('enrollment/', views.FaceEnrollmentView.as_view(), name='enrollment'),
    path('enrollment/capture/', views.FaceEnrollmentCaptureView.as_view(), name='enrollment_capture'),
    path('enrollment/process/', views.ProcessFaceEnrollmentView.as_view(), name='process_enrollment'),

    # Face recognition for attendance
    path('recognize/', views.FaceRecognitionView.as_view(), name='recognize'),
    path('recognize/process/', views.ProcessFaceRecognitionView.as_view(), name='process_recognition'),

    # Face management
    path('encodings/', views.FaceEncodingListView.as_view(), name='encoding_list'),
    path('encodings/<uuid:pk>/delete/', views.FaceEncodingDeleteView.as_view(), name='encoding_delete'),
    path('encodings/<uuid:encoding_id>/delete/', views.delete_face_encoding, name='delete_encoding'),

    # Statistics and analytics
    path('stats/', views.face_recognition_stats, name='stats'),

    # API endpoints
    path('api/capture/', views.CaptureImageAPIView.as_view(), name='api_capture'),
    path('api/recognize/', views.RecognizeImageAPIView.as_view(), name='api_recognize'),
    path('api/enroll/', views.EnrollFaceAPIView.as_view(), name='api_enroll'),
]
