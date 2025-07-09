from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from .models import Student, Subject, Attendance, Result, Teacher, Admin
from datetime import date
import json

# Authentication Views
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if hasattr(user, 'admin'):
                messages.success(request, 'Welcome Admin!')
                return redirect('admin_dashboard')
            elif hasattr(user, 'teacher'):
                messages.success(request, 'Welcome Teacher!')
                return redirect('teacher_dashboard')
            elif hasattr(user, 'student'):
                messages.success(request, 'Welcome Student!')
                return redirect('student_dashboard')
            else:
                messages.error(request, 'Your account is not properly configured. Please contact support.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        # Validation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'registration/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'registration/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'registration/register.html')
        
        try:
            # Create User
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            
            # Only create Admin profile (no student/teacher registration)
            admin_id = request.POST.get('admin_id', f'ADM{user.id:03d}')
            phone = request.POST.get('phone', '')
            
            Admin.objects.create(
                user=user,
                admin_id=admin_id,
                phone=phone
            )
            messages.success(request, 'Admin account created successfully! Please login.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    return render(request, 'registration/register.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

# Admin Views
@login_required
def admin_dashboard(request):
    # Simple check - if user doesn't have admin profile, redirect to login
    if not hasattr(request.user, 'admin'):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('login')
    
    context = {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_subjects': Subject.objects.count(),
        'blocked_students': Student.objects.filter(is_blocked=True).count(),
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def admin_register_teacher(request):
    # Simple check - if user doesn't have admin profile, redirect to login
    if not hasattr(request.user, 'admin'):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('login')
    
    if request.method == 'POST':
        # Get form data
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        employee_id = request.POST['employee_id']
        phone = request.POST['phone']
        subject_ids = request.POST.getlist('subjects')
        
        try:
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                subjects = Subject.objects.all()
                return render(request, 'admin/register_teacher.html', {'subjects': subjects})
            
            # Check if employee_id already exists
            if Teacher.objects.filter(employee_id=employee_id).exists():
                messages.error(request, 'Employee ID already exists.')
                subjects = Subject.objects.all()
                return render(request, 'admin/register_teacher.html', {'subjects': subjects})
            
            # Create User
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            
            # Create Teacher
            teacher = Teacher.objects.create(
                user=user,
                employee_id=employee_id,
                phone=phone
            )
            
            # Assign subjects
            if subject_ids:
                teacher.subjects.set(subject_ids)
            
            messages.success(request, f'Teacher {first_name} {last_name} registered successfully!')
            return redirect('admin_teachers')
        except Exception as e:
            messages.error(request, f'Error registering teacher: {str(e)}')
    
    subjects = Subject.objects.all()
    return render(request, 'admin/register_teacher.html', {'subjects': subjects})

@login_required
def admin_register_student(request):
    # Simple check - if user doesn't have admin profile, redirect to login
    if not hasattr(request.user, 'admin'):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('login')
    
    if request.method == 'POST':
        # Get form data
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        student_id = request.POST['student_id']
        phone = request.POST['phone']
        address = request.POST['address']
        date_of_birth = request.POST['date_of_birth']
        subject_ids = request.POST.getlist('subjects')
        
        try:
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                subjects = Subject.objects.all()
                return render(request, 'admin/register_student.html', {'subjects': subjects})
            
            # Check if student_id already exists
            if Student.objects.filter(student_id=student_id).exists():
                messages.error(request, 'Student ID already exists.')
                subjects = Subject.objects.all()
                return render(request, 'admin/register_student.html', {'subjects': subjects})
            
            # Create User
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            
            # Create Student
            student = Student.objects.create(
                user=user,
                student_id=student_id,
                phone=phone,
                address=address,
                date_of_birth=date_of_birth if date_of_birth else None
            )
            
            # Assign subjects
            if subject_ids:
                student.subjects.set(subject_ids)
            
            messages.success(request, f'Student {first_name} {last_name} registered successfully!')
            return redirect('admin_students')
        except Exception as e:
            messages.error(request, f'Error registering student: {str(e)}')
    
    subjects = Subject.objects.all()
    return render(request, 'admin/register_student.html', {'subjects': subjects})

@login_required
def admin_teachers(request):
    # Simple check - if user doesn't have admin profile, redirect to login
    if not hasattr(request.user, 'admin'):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('login')
    
    teachers = Teacher.objects.all().order_by('employee_id')
    return render(request, 'admin/teachers.html', {'teachers': teachers})

@login_required
def admin_students(request):
    # Simple check - if user doesn't have admin profile, redirect to login
    if not hasattr(request.user, 'admin'):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('login')
    
    students = Student.objects.all().order_by('student_id')
    return render(request, 'admin/students.html', {'students': students})

@login_required
def admin_subjects(request):
    # Simple check - if user doesn't have admin profile, redirect to login
    if not hasattr(request.user, 'admin'):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('login')
    
    subjects = Subject.objects.all()
    return render(request, 'admin/subjects.html', {'subjects': subjects})

@login_required
def admin_add_subject(request):
    # Simple check - if user doesn't have admin profile, redirect to login
    if not hasattr(request.user, 'admin'):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('login')
    
    if request.method == 'POST':
        name = request.POST['name']
        code = request.POST['code']
        description = request.POST['description']
        
        try:
            # Check if subject code already exists
            if Subject.objects.filter(code=code).exists():
                messages.error(request, 'Subject code already exists.')
                return render(request, 'admin/add_subject.html')
            
            Subject.objects.create(
                name=name,
                code=code,
                description=description
            )
            messages.success(request, 'Subject added successfully!')
            return redirect('admin_subjects')
        except Exception as e:
            messages.error(request, f'Error adding subject: {str(e)}')
    
    return render(request, 'admin/add_subject.html')

@login_required
def admin_block_student(request, student_id):
    # Simple check - if user doesn't have admin profile, redirect to login
    if not hasattr(request.user, 'admin'):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('login')
    
    student = get_object_or_404(Student, id=student_id)
    student.is_blocked = not student.is_blocked
    student.save()
    
    status = "blocked" if student.is_blocked else "unblocked"
    messages.success(request, f'Student {status} successfully!')
    return redirect('admin_students')

@login_required
def admin_assign_subjects_teacher(request, teacher_id):
    # Simple check - if user doesn't have admin profile, redirect to login
    if not hasattr(request.user, 'admin'):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('login')
    
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    if request.method == 'POST':
        subject_ids = request.POST.getlist('subjects')
        teacher.subjects.set(subject_ids)
        messages.success(request, f'Subjects assigned to {teacher.user.first_name} {teacher.user.last_name} successfully!')
        return redirect('admin_teachers')
    
    subjects = Subject.objects.all()
    assigned_subjects = teacher.subjects.all()
    
    return render(request, 'admin/assign_subjects_teacher.html', {
        'teacher': teacher,
        'subjects': subjects,
        'assigned_subjects': assigned_subjects
    })

# Teacher Views
@login_required
def teacher_dashboard(request):
    # Simple check - if user doesn't have teacher profile, redirect to login
    if not hasattr(request.user, 'teacher'):
        messages.error(request, 'Access denied. Teacher privileges required.')
        return redirect('login')
    
    teacher = request.user.teacher
    teacher_subjects = teacher.subjects.all()
    
    # Get students who share subjects with this teacher
    students = Student.objects.filter(
        subjects__in=teacher_subjects,
        is_blocked=False
    ).distinct()
    
    context = {
        'teacher': teacher,
        'my_subjects': teacher_subjects,
        'my_students': students.count(),
        'today_attendance': Attendance.objects.filter(
            date=date.today(),
            subject__in=teacher_subjects
        ).count(),
    }
    return render(request, 'teacher/dashboard.html', context)

@login_required
def teacher_students(request):
    # Simple check - if user doesn't have teacher profile, redirect to login
    if not hasattr(request.user, 'teacher'):
        messages.error(request, 'Access denied. Teacher privileges required.')
        return redirect('login')
    
    teacher = request.user.teacher
    teacher_subjects = teacher.subjects.all()
    
    # Only show students who share subjects with this teacher
    students = Student.objects.filter(
        subjects__in=teacher_subjects,
        is_blocked=False
    ).distinct().order_by('student_id')
    
    return render(request, 'teacher/students.html', {
        'students': students,
        'teacher_subjects': teacher_subjects
    })

@login_required
def teacher_attendance(request):
    # Simple check - if user doesn't have teacher profile, redirect to login
    if not hasattr(request.user, 'teacher'):
        messages.error(request, 'Access denied. Teacher privileges required.')
        return redirect('login')
    
    teacher = request.user.teacher
    teacher_subjects = teacher.subjects.all()
    
    # Get students for selected subject
    selected_subject_id = request.GET.get('subject_id')
    selected_date = request.GET.get('date', str(date.today()))
    
    students = []
    today_attendance = {}
    
    if selected_subject_id:
        # Verify teacher teaches this subject
        if not teacher_subjects.filter(id=selected_subject_id).exists():
            messages.error(request, 'You are not authorized to mark attendance for this subject.')
            return redirect('teacher_attendance')
        
        # Only show students who have this subject
        students = Student.objects.filter(
            subjects__id=selected_subject_id,
            is_blocked=False
        ).order_by('student_id')
        
        # Get existing attendance - convert to dictionary with student.id as key
        attendance_records = Attendance.objects.filter(
            subject_id=selected_subject_id,
            date=selected_date
        )
        
        for record in attendance_records:
            today_attendance[record.student.id] = record.is_present
    
    context = {
        'subjects': teacher_subjects,
        'students': students,
        'today_attendance': today_attendance,
        'selected_subject': selected_subject_id,
        'selected_date': selected_date,
    }
    return render(request, 'teacher/attendance.html', context)

@login_required
def teacher_mark_attendance(request):
    # Simple check - if user doesn't have teacher profile, redirect to login
    if not hasattr(request.user, 'teacher'):
        messages.error(request, 'Access denied. Teacher privileges required.')
        return redirect('login')
    
    if request.method == 'POST':
        subject_id = request.POST['subject_id']
        attendance_date = request.POST['date']
        attendance_data = request.POST.getlist('attendance')
        
        teacher = request.user.teacher
        subject = get_object_or_404(Subject, id=subject_id)
        
        # Verify teacher teaches this subject
        if subject not in teacher.subjects.all():
            messages.error(request, 'You are not authorized to mark attendance for this subject.')
            return redirect('teacher_attendance')
        
        # Clear existing attendance for this date and subject
        Attendance.objects.filter(subject=subject, date=attendance_date).delete()
        
        # Mark new attendance
        students = Student.objects.filter(
            subjects=subject,
            is_blocked=False
        )
        
        for student in students:
            is_present = str(student.id) in attendance_data
            Attendance.objects.create(
                student=student,
                subject=subject,
                date=attendance_date,
                is_present=is_present,
                marked_by=request.user
            )
        
        messages.success(request, 'Attendance marked successfully!')
        return redirect('teacher_attendance')
    
    return redirect('teacher_attendance')

@login_required
def teacher_results(request):
    # Simple check - if user doesn't have teacher profile, redirect to login
    if not hasattr(request.user, 'teacher'):
        messages.error(request, 'Access denied. Teacher privileges required.')
        return redirect('login')
    
    teacher = request.user.teacher
    teacher_subjects = teacher.subjects.all()
    
    # Only show results for subjects this teacher teaches
    results = Result.objects.filter(
        subject__in=teacher_subjects
    ).order_by('-created_at')
    
    return render(request, 'teacher/results.html', {'results': results})

@login_required
def teacher_add_result(request):
    # Simple check - if user doesn't have teacher profile, redirect to login
    if not hasattr(request.user, 'teacher'):
        messages.error(request, 'Access denied. Teacher privileges required.')
        return redirect('login')
    
    teacher = request.user.teacher
    teacher_subjects = teacher.subjects.all()
    
    if request.method == 'POST':
        student_id = request.POST['student_id']
        subject_id = request.POST['subject_id']
        exam_type = request.POST['exam_type']
        marks_obtained = request.POST['marks_obtained']
        total_marks = request.POST['total_marks']
        exam_date = request.POST['exam_date']
        
        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)
        
        # Verify teacher teaches this subject
        if subject not in teacher_subjects:
            messages.error(request, 'You are not authorized to add results for this subject.')
            return redirect('teacher_results')
        
        # Verify student is enrolled in this subject
        if subject not in student.subjects.all():
            messages.error(request, 'This student is not enrolled in the selected subject.')
            return redirect('teacher_add_result')
        
        Result.objects.create(
            student=student,
            subject=subject,
            exam_type=exam_type,
            marks_obtained=marks_obtained,
            total_marks=total_marks,
            exam_date=exam_date
        )
        
        messages.success(request, 'Result added successfully!')
        return redirect('teacher_results')
    
    # Only show students who share subjects with this teacher
    students = Student.objects.filter(
        subjects__in=teacher_subjects,
        is_blocked=False
    ).distinct()
    
    context = {
        'students': students,
        'subjects': teacher_subjects,
    }
    return render(request, 'teacher/add_result.html', context)

# Student Views
@login_required
def student_dashboard(request):
    # Simple check - if user doesn't have student profile, redirect to login
    if not hasattr(request.user, 'student'):
        messages.error(request, 'Access denied. Student privileges required.')
        return redirect('login')
    
    student = request.user.student
    student_subjects = student.subjects.all()
    
    # Get attendance records
    total_classes = Attendance.objects.filter(
        student=student,
        subject__in=student_subjects
    ).count()
    
    present_classes = Attendance.objects.filter(
        student=student,
        subject__in=student_subjects,
        is_present=True
    ).count()
    
    attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
    
    # Get recent results
    recent_results = Result.objects.filter(
        student=student
    ).order_by('-created_at')[:5]
    
    context = {
        'student': student,
        'my_subjects': student_subjects,
        'total_classes': total_classes,
        'present_classes': present_classes,
        'attendance_percentage': attendance_percentage,
        'recent_results': recent_results,
    }
    return render(request, 'student/dashboard.html', context)
