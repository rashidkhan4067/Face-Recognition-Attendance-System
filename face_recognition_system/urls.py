"""
URL configuration for face_recognition_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/auth/login/', permanent=False), name='home'),
    path('auth/', include('authentication.urls')),
    path('face/', include('face_recognition.urls')),
    path('attendance/', include('attendance.urls')),
    # Comment out allauth URLs to avoid conflicts
    # path('accounts/', include('allauth.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
