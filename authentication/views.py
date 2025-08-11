from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import (
    TemplateView, CreateView, UpdateView, DeleteView,
    ListView, DetailView, FormView
)
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta

from .models import CustomUser, Department
from attendance.models import AttendanceRecord
from face_recognition.models import FaceRecognitionLog
from .forms import (
    CustomUserCreationForm, CustomUserChangeForm,
    ProfileForm, DepartmentForm, CustomAuthenticationForm
)


class CustomLoginView(FormView):
    """Custom login view"""
    template_name = 'authentication/login.html'
    form_class = CustomAuthenticationForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        # Handle remember me
        if not form.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(0)

        messages.success(self.request, f'Welcome back, {user.get_full_name() or user.username}!')
        return redirect(self.get_success_url())

    def get_success_url(self):
        # Get the 'next' parameter from the URL, or default to dashboard
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('authentication:dashboard')


class CustomLogoutView(LogoutView):
    """Custom logout view"""
    next_page = reverse_lazy('authentication:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)


class RegisterView(CreateView):
    """User registration view"""
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'authentication/register.html'
    success_url = reverse_lazy('authentication:login')

    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users to dashboard
        if request.user.is_authenticated:
            return redirect('authentication:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.filter(is_active=True)
        context['page_title'] = 'Create Account'
        context['page_description'] = 'Join the Face Recognition Attendance System'
        return context

    def form_valid(self, form):
        # Set default values for new users
        user = form.save(commit=False)
        user.is_active = True  # Auto-activate new users
        user.is_face_enrolled = False  # Will need to enroll later
        user.save()

        # Create success message with next steps
        messages.success(
            self.request,
            f'Welcome {user.get_full_name()}! Your account has been created successfully. '
            f'Please log in and complete your face enrollment for attendance tracking.'
        )

        # Log the registration
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f'New user registered: {user.username} ({user.employee_id})')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Please correct the errors below and try again.'
        )
        return super().form_invalid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view"""
    template_name = 'authentication/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get recent attendance records
        recent_attendance = AttendanceRecord.objects.filter(
            user=user
        ).order_by('-date')[:5]

        # Get today's attendance
        today = timezone.now().date()
        today_attendance = AttendanceRecord.objects.filter(
            user=user, date=today
        ).first()

        # Calculate this month's statistics
        current_month = timezone.now().replace(day=1)
        monthly_attendance = AttendanceRecord.objects.filter(
            user=user,
            date__gte=current_month
        )

        context.update({
            'recent_attendance': recent_attendance,
            'today_attendance': today_attendance,
            'monthly_present_days': monthly_attendance.filter(status='present').count(),
            'monthly_late_days': monthly_attendance.filter(status='late').count(),
            'monthly_absent_days': monthly_attendance.filter(status='absent').count(),
            'face_enrolled': user.is_face_enrolled,
            'face_encodings_count': user.active_face_encodings_count,
        })

        return context


class ProfileView(LoginRequiredMixin, DetailView):
    """User profile view"""
    model = CustomUser
    template_name = 'authentication/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user


class EditProfileView(LoginRequiredMixin, UpdateView):
    """Edit user profile view"""
    model = CustomUser
    form_class = ProfileForm
    template_name = 'authentication/edit_profile.html'
    success_url = reverse_lazy('authentication:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to require admin role"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['admin', 'manager']


class UserListView(AdminRequiredMixin, ListView):
    """List all users (admin/manager only)"""
    model = CustomUser
    template_name = 'authentication/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = CustomUser.objects.select_related('department')
        search = self.request.GET.get('search')
        department = self.request.GET.get('department')
        role = self.request.GET.get('role')

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(email__icontains=search)
            )

        if department:
            queryset = queryset.filter(department_id=department)

        if role:
            queryset = queryset.filter(role=role)

        return queryset.order_by('employee_id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        context['roles'] = CustomUser.USER_ROLES
        return context


class UserCreateView(AdminRequiredMixin, CreateView):
    """Create new user (admin/manager only)"""
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'authentication/user_form.html'
    success_url = reverse_lazy('authentication:user_list')

    def form_valid(self, form):
        messages.success(self.request, f'User {form.instance.employee_id} created successfully!')
        return super().form_valid(form)


class UserDetailView(AdminRequiredMixin, DetailView):
    """User detail view (admin/manager only)"""
    model = CustomUser
    template_name = 'authentication/user_detail.html'
    context_object_name = 'user_detail'


class UserUpdateView(AdminRequiredMixin, UpdateView):
    """Update user (admin/manager only)"""
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'authentication/user_form.html'

    def get_success_url(self):
        return reverse('authentication:user_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'User {form.instance.employee_id} updated successfully!')
        return super().form_valid(form)


class UserDeleteView(AdminRequiredMixin, DeleteView):
    """Delete user (admin only)"""
    model = CustomUser
    template_name = 'authentication/user_confirm_delete.html'
    success_url = reverse_lazy('authentication:user_list')

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'admin'

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        messages.success(request, f'User {user.employee_id} deleted successfully!')
        return super().delete(request, *args, **kwargs)


class DepartmentListView(AdminRequiredMixin, ListView):
    """List all departments"""
    model = Department
    template_name = 'authentication/department_list.html'
    context_object_name = 'departments'

    def get_queryset(self):
        return Department.objects.annotate(
            user_count=Count('customuser')
        ).order_by('name')


class DepartmentCreateView(AdminRequiredMixin, CreateView):
    """Create new department"""
    model = Department
    form_class = DepartmentForm
    template_name = 'authentication/department_form.html'
    success_url = reverse_lazy('authentication:department_list')

    def form_valid(self, form):
        messages.success(self.request, f'Department {form.instance.name} created successfully!')
        return super().form_valid(form)


class DepartmentUpdateView(AdminRequiredMixin, UpdateView):
    """Update department"""
    model = Department
    form_class = DepartmentForm
    template_name = 'authentication/department_form.html'
    success_url = reverse_lazy('authentication:department_list')

    def form_valid(self, form):
        messages.success(self.request, f'Department {form.instance.name} updated successfully!')
        return super().form_valid(form)


class SettingsView(LoginRequiredMixin, TemplateView):
    """User settings view"""
    template_name = 'authentication/settings.html'


class AnalyticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Analytics dashboard view"""
    template_name = 'authentication/analytics.html'

    def test_func(self):
        # Only allow admin and manager roles to access analytics
        return self.request.user.role in ['admin', 'manager']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get analytics data
        from .models import AttendanceRecord
        from .models import FaceRecognitionLog

        # User statistics
        total_users = CustomUser.objects.count()
        active_users = CustomUser.objects.filter(is_active=True).count()
        face_enrolled_users = CustomUser.objects.filter(is_face_enrolled=True).count()

        # Department statistics
        total_departments = Department.objects.count()
        active_departments = Department.objects.filter(is_active=True).count()

        # Attendance statistics (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now().date() - timedelta(days=30)

        recent_attendance = AttendanceRecord.objects.filter(
            date__gte=thirty_days_ago
        )

        total_attendance_records = recent_attendance.count()
        present_records = recent_attendance.filter(status__in=['present', 'late']).count()
        attendance_rate = (present_records / total_attendance_records * 100) if total_attendance_records > 0 else 0

        # Face recognition statistics
        recent_face_logs = FaceRecognitionLog.objects.filter(
            timestamp__gte=thirty_days_ago
        )

        total_face_attempts = recent_face_logs.count()
        successful_face_recognition = recent_face_logs.filter(result='success').count()
        face_success_rate = (successful_face_recognition / total_face_attempts * 100) if total_face_attempts > 0 else 0

        # Department performance
        department_stats = []
        for dept in Department.objects.filter(is_active=True):
            dept_users = CustomUser.objects.filter(department=dept, is_active=True).count()
            dept_attendance = recent_attendance.filter(user__department=dept)
            dept_present = dept_attendance.filter(status__in=['present', 'late']).count()
            dept_rate = (dept_present / dept_attendance.count() * 100) if dept_attendance.count() > 0 else 0

            department_stats.append({
                'name': dept.name,
                'users': dept_users,
                'attendance_rate': round(dept_rate, 1)
            })

        context.update({
            'total_users': total_users,
            'active_users': active_users,
            'face_enrolled_users': face_enrolled_users,
            'face_enrollment_rate': round((face_enrolled_users / active_users * 100) if active_users > 0 else 0, 1),
            'total_departments': total_departments,
            'active_departments': active_departments,
            'attendance_rate': round(attendance_rate, 1),
            'face_success_rate': round(face_success_rate, 1),
            'total_attendance_records': total_attendance_records,
            'total_face_attempts': total_face_attempts,
            'department_stats': department_stats,
        })

        return context


@login_required
def profile_view(request):
    """User profile view"""
    context = {
        'profile_user': request.user,
        'face_encodings_count': 0,  # Placeholder
        'monthly_present_days': 22,  # Placeholder
    }
    return render(request, 'authentication/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('authentication:profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'authentication/edit_profile.html', {'form': form})
