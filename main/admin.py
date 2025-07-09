from django.contrib import admin
from .models import Student, Subject, Attendance, Result, Teacher, Admin

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ['admin_id', 'get_full_name', 'phone', 'created_at']
    list_filter = ['created_at']
    search_fields = ['admin_id', 'user__first_name', 'user__last_name', 'user__email']
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Full Name'

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'get_full_name', 'phone', 'get_subjects', 'created_at']
    list_filter = ['created_at', 'subjects']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'user__email']
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Full Name'
    
    def get_subjects(self, obj):
        return ", ".join([subject.code for subject in obj.subjects.all()])
    get_subjects.short_description = 'Subjects'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'get_full_name', 'phone', 'is_blocked', 'created_at']
    list_filter = ['is_blocked', 'created_at']
    search_fields = ['student_id', 'user__first_name', 'user__last_name', 'user__email']
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Full Name'

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description']
    search_fields = ['name', 'code']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'date', 'is_present', 'marked_by']
    list_filter = ['is_present', 'date', 'subject']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'subject__name']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'exam_type', 'marks_obtained', 'total_marks', 'get_percentage', 'get_grade']
    list_filter = ['exam_type', 'subject', 'exam_date']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'subject__name']
