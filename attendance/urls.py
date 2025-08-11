from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Attendance marking
    path('check/', views.AttendanceCheckView.as_view(), name='check'),
    path('check/manual/', views.ManualAttendanceView.as_view(), name='manual_check'),
    
    # Attendance history and reports
    path('history/', views.AttendanceHistoryView.as_view(), name='history'),
    path('reports/', views.AttendanceReportsView.as_view(), name='reports'),
    path('reports/export/', views.ExportAttendanceView.as_view(), name='export'),
    
    # Leave management
    path('leave/', views.LeaveRequestListView.as_view(), name='leave_list'),
    path('leave/create/', views.LeaveRequestCreateView.as_view(), name='leave_create'),
    path('leave/<uuid:pk>/', views.LeaveRequestDetailView.as_view(), name='leave_detail'),
    path('leave/<uuid:pk>/approve/', views.ApproveLeaveView.as_view(), name='leave_approve'),
    path('leave/<uuid:pk>/reject/', views.RejectLeaveView.as_view(), name='leave_reject'),
    
    # Settings
    path('settings/', views.AttendanceSettingsView.as_view(), name='settings'),
    
    # API endpoints
    path('api/mark/', views.MarkAttendanceAPIView.as_view(), name='api_mark'),
    path('api/status/', views.AttendanceStatusAPIView.as_view(), name='api_status'),
    path('api/stats/', views.AttendanceStatsAPIView.as_view(), name='api_stats'),
]
