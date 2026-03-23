from django.urls import path
from . import views
from internship_app import views as internship_views

urlpatterns = [

    # ---------------- HOME ----------------
    path('', views.home, name='home'),

    # ---------------- AUTHENTICATION ----------------
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),

    # ---------------- PROFILE ----------------
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='edit_profile'),

    # ---------------- STUDENT APPROVALS ----------------
    path('pending-students/', views.pending_students, name='pending_students'),
    path('approve-student/<int:student_id>/', views.approve_student, name='approve_student'),
    path('reject-student/<int:student_id>/', views.reject_student, name='reject_student'),

    # ---------------- FACULTY APPROVALS ----------------
    path('pending-faculty/', views.pending_faculty, name='pending_faculty'),
    path('approve-faculty/<int:faculty_id>/', views.approve_faculty, name='approve_faculty'),
    path('reject-faculty/<int:faculty_id>/', views.reject_faculty, name='reject_faculty'),

    # ---------------- DASHBOARDS (use internship_app views with full data) ----------------
    path('dashboard/student/', internship_views.student_dashboard, name='student_dashboard'),
    path('dashboard/faculty/', internship_views.faculty_dashboard, name='faculty_dashboard'),
    path('dashboard/admin/', internship_views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/hod/', internship_views.admin_dashboard, name='hod_dashboard'),
    path('dashboard/export/', internship_views.export_dashboard_csv, name='export_dashboard_csv'),

]