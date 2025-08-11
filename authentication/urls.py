from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Authentication views
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # User management (admin/manager only)
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<uuid:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    path('users/<uuid:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),

    # Department management
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<uuid:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_edit'),

    # Settings
    path('settings/', views.SettingsView.as_view(), name='settings'),

    # Analytics
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
]
