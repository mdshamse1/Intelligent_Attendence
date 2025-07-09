from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/register-teacher/', views.admin_register_teacher, name='admin_register_teacher'),
    path('admin/register-student/', views.admin_register_student, name='admin_register_student'),
    path('admin/teachers/', views.admin_teachers, name='admin_teachers'),
    path('admin/students/', views.admin_students, name='admin_students'),
    path('admin/subjects/', views.admin_subjects, name='admin_subjects'),
    path('admin/add-subject/', views.admin_add_subject, name='admin_add_subject'),
    path('admin/block-student/<int:student_id>/', views.admin_block_student, name='admin_block_student'),
    path('admin/assign-subjects-teacher/<int:teacher_id>/', views.admin_assign_subjects_teacher, name='admin_assign_subjects_teacher'),
    
    # Teacher URLs
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/students/', views.teacher_students, name='teacher_students'),
    path('teacher/attendance/', views.teacher_attendance, name='teacher_attendance'),
    path('teacher/mark-attendance/', views.teacher_mark_attendance, name='teacher_mark_attendance'),
    path('teacher/results/', views.teacher_results, name='teacher_results'),
    path('teacher/add-result/', views.teacher_add_result, name='teacher_add_result'),
    
    # Student URLs
    path('', views.student_dashboard, name='student_dashboard'),
]
