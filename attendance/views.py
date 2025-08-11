from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import AttendanceRecord
from authentication.models import CustomUser


class AttendanceCheckView(LoginRequiredMixin, TemplateView):
    """Attendance check-in/out view"""
    template_name = 'attendance/check.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get today's attendance record
        today = timezone.now().date()
        try:
            today_record = AttendanceRecord.objects.get(
                user=self.request.user,
                date=today
            )
            context['today_record'] = today_record
        except AttendanceRecord.DoesNotExist:
            context['today_record'] = None

        return context


class AttendanceHistoryView(LoginRequiredMixin, ListView):
    """Attendance history view"""
    model = AttendanceRecord
    template_name = 'attendance/history.html'
    context_object_name = 'attendance_records'
    paginate_by = 20

    def get_queryset(self):
        queryset = AttendanceRecord.objects.filter(
            user=self.request.user
        ).order_by('-date')

        # Date range filter
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass

        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset


class AttendanceReportsView(LoginRequiredMixin, TemplateView):
    """Attendance reports view"""
    template_name = 'attendance/reports.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get report parameters
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        report_type = self.request.GET.get('report_type', 'summary')

        # Calculate statistics
        context['total_present_days'] = 22  # Placeholder
        context['total_absent_days'] = 1    # Placeholder
        context['total_late_days'] = 3      # Placeholder
        context['total_working_hours'] = 176 # Placeholder
        context['attendance_rate'] = 95.7   # Placeholder
        context['average_daily_hours'] = 8.2 # Placeholder

        return context


class ManualAttendanceView(LoginRequiredMixin, TemplateView):
    """Manual attendance view"""
    template_name = 'attendance/manual_check.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any necessary context here
        return context

class AttendanceReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/reports.html'

class ExportAttendanceView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/export.html'

class LeaveRequestListView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/leave_list.html'

class LeaveRequestCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/leave_create.html'

class LeaveRequestDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/leave_detail.html'

class ApproveLeaveView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/leave_approve.html'

class RejectLeaveView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/leave_reject.html'

class AttendanceSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/settings.html'

class MarkAttendanceAPIView(APIView):
    """API for marking attendance"""

    def post(self, request):
        try:
            data = request.data
            attendance_type = data.get('type')  # 'check_in' or 'check_out'
            method = data.get('method', 'manual')  # 'face_recognition' or 'manual'
            notes = data.get('notes', '')

            if not attendance_type or attendance_type not in ['check_in', 'check_out']:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid attendance type'
                }, status=400)

            # Get or create today's attendance record
            today = timezone.now().date()
            attendance_record, created = AttendanceRecord.objects.get_or_create(
                user=request.user,
                date=today,
                defaults={
                    'status': 'absent',
                    'working_hours': 0.0
                }
            )

            current_time = timezone.now()

            if attendance_type == 'check_in':
                if attendance_record.check_in_time:
                    return JsonResponse({
                        'success': False,
                        'error': 'Already checked in today'
                    }, status=400)

                attendance_record.check_in_time = current_time
                attendance_record.check_in_method = method
                attendance_record.status = 'present'

                # Check if late (assuming work starts at 9:00 AM)
                work_start_time = current_time.replace(hour=9, minute=0, second=0, microsecond=0)
                if current_time > work_start_time:
                    attendance_record.status = 'late'

            elif attendance_type == 'check_out':
                if not attendance_record.check_in_time:
                    return JsonResponse({
                        'success': False,
                        'error': 'Must check in first'
                    }, status=400)

                if attendance_record.check_out_time:
                    return JsonResponse({
                        'success': False,
                        'error': 'Already checked out today'
                    }, status=400)

                attendance_record.check_out_time = current_time
                attendance_record.check_out_method = method

                # Calculate working hours
                time_diff = current_time - attendance_record.check_in_time
                working_hours = time_diff.total_seconds() / 3600
                attendance_record.working_hours = round(working_hours, 2)

            if notes:
                attendance_record.notes = notes

            attendance_record.save()

            return JsonResponse({
                'success': True,
                'message': f'Successfully {attendance_type.replace("_", " ")}',
                'data': {
                    'type': attendance_type,
                    'time': current_time.strftime('%H:%M'),
                    'status': attendance_record.status,
                    'working_hours': attendance_record.working_hours
                }
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class AttendanceStatusAPIView(APIView):
    """API for getting attendance status"""

    def get(self, request):
        try:
            today = timezone.now().date()

            try:
                attendance_record = AttendanceRecord.objects.get(
                    user=request.user,
                    date=today
                )

                return JsonResponse({
                    'success': True,
                    'data': {
                        'date': today.isoformat(),
                        'check_in_time': attendance_record.check_in_time.strftime('%H:%M') if attendance_record.check_in_time else None,
                        'check_out_time': attendance_record.check_out_time.strftime('%H:%M') if attendance_record.check_out_time else None,
                        'working_hours': attendance_record.working_hours,
                        'status': attendance_record.status,
                        'notes': attendance_record.notes,
                        'can_check_in': not attendance_record.check_in_time,
                        'can_check_out': attendance_record.check_in_time and not attendance_record.check_out_time
                    }
                })

            except AttendanceRecord.DoesNotExist:
                return JsonResponse({
                    'success': True,
                    'data': {
                        'date': today.isoformat(),
                        'check_in_time': None,
                        'check_out_time': None,
                        'working_hours': 0.0,
                        'status': 'absent',
                        'notes': '',
                        'can_check_in': True,
                        'can_check_out': False
                    }
                })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class AttendanceStatsAPIView(APIView):
    """API for getting attendance statistics"""

    def get(self, request):
        try:
            # Get date range (default to current month)
            today = timezone.now().date()
            start_of_month = today.replace(day=1)

            # Get user's attendance records for the month
            records = AttendanceRecord.objects.filter(
                user=request.user,
                date__gte=start_of_month,
                date__lte=today
            )

            # Calculate statistics
            total_days = records.count()
            present_days = records.filter(status__in=['present', 'late']).count()
            absent_days = records.filter(status='absent').count()
            late_days = records.filter(status='late').count()

            total_hours = sum(record.working_hours for record in records)
            avg_hours = total_hours / present_days if present_days > 0 else 0

            attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0

            return JsonResponse({
                'success': True,
                'data': {
                    'total_days': total_days,
                    'present_days': present_days,
                    'absent_days': absent_days,
                    'late_days': late_days,
                    'total_hours': round(total_hours, 2),
                    'average_hours': round(avg_hours, 2),
                    'attendance_rate': round(attendance_rate, 2)
                }
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

class ManualAttendanceView(LoginRequiredMixin, TemplateView):
    """Manual attendance view"""
    template_name = 'attendance/manual_check.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any necessary context here
        return context
