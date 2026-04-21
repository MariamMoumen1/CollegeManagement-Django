import json
import requests
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .EmailBackend import EmailBackend
from .models import Attendance, Session, Subject
from .models import Parent, AttendanceReport, StudentResult, Student

# ===========================
# 🔐 LOGIN SYSTEM FIX
# ===========================

def login_page(request):

    if request.user.is_authenticated:

        if request.user.user_type == '1':
            return redirect("admin_home")

        elif request.user.user_type == '2':
            return redirect("staff_home")

        elif request.user.user_type == '3':
            return redirect("student_home")

        elif request.user.user_type == '4':
            return redirect("parent_home")

        return HttpResponse("User type not valid")
    # ✅ CORRECT:
    return render(request, 'main_app/login.html')


def doLogin(request):

    if request.method != 'POST':
        return HttpResponse("Method Not Allowed")

    email = request.POST.get('email')
    password = request.POST.get('password')

    # ⚠️ CAPTCHA OPTIONNEL (désactivé pour éviter erreurs)
    # Tu peux remettre plus tard

    user = EmailBackend.authenticate(
        request,
        username=email,
        password=password
    )

    if user is not None:
        login(request, user)

        if user.user_type == '1':
            return redirect("admin_home")

        elif user.user_type == '2':
            return redirect("staff_home")

        elif user.user_type == '3':
            return redirect("student_home")

        elif user.user_type == '4':
            return redirect("parent_home")

    messages.error(request, "Invalid email or password")
    return redirect("login")


def logout_user(request):
    logout(request)
    return redirect('/')

# ===========================
# 📊 AJAX ATTENDANCE
# ===========================

@csrf_exempt
def get_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')

    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)

        attendance = Attendance.objects.filter(subject=subject, session=session)

        data = []
        for att in attendance:
            data.append({
                "id": att.id,
                "attendance_date": str(att.date),
                "session": att.session.id
            })

        return JsonResponse(data, safe=False)

    except Exception:
        return JsonResponse([], safe=False)


# ===========================
# 🔒 PARENT PERMISSION FIX
# ===========================

from django.contrib.auth.decorators import login_required
from functools import wraps

def parent_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.user_type != '4':
            logout(request)
            return redirect("login")

        return view_func(request, *args, **kwargs)

    return wrapper


# ===========================
# 👨‍👩‍👦 PARENT VIEWS
# ===========================

@login_required
@parent_required
def parent_home(request):
    parent = Parent.objects.get(admin=request.user)

    return render(request, "parent_template/home.html", {
        "student": parent.student
    })


from django.shortcuts import render
from .models import Student, AttendanceReport


def parent_attendance(request):

    student = Student.objects.filter(parent__admin=request.user).first()

    attendance_reports = AttendanceReport.objects.filter(student=student)

    data = []
    present = 0
    absent = 0

    for att in attendance_reports:

        # 🔥 FIX ICI (sécurisé)
        date_value = getattr(att.attendance_id, "date", None)

        data.append({
            "date": date_value,
            "status": att.status
        })

        if att.status:
            present += 1
        else:
            absent += 1

    return render(request, "parent_template/attendance.html", {
        "student": student,
        "attendance": data,
        "present": present,
        "absent": absent
    })

from django.shortcuts import render
from .models import Student, Subject, StudentResult


def parent_result(request):

    student = Student.objects.filter(parent__admin=request.user).first()

    if not student:
        return render(request, "parent/result.html", {
            "error": "Aucun étudiant trouvé"
        })

    results = StudentResult.objects.filter(student=student)

    data = []
    total = 0
    count = 0

    for r in results:
        test = r.test
        exam = r.exam
        final = test + exam

        data.append({
            "subject": r.subject.name,
            "test": test,
            "exam": exam,
            "total": final
        })

        total += final
        count += 1

    avg = total / count if count > 0 else 0

    return render(request, "parent_template/result.html", {
        "student": student,
        "results": data,
        "average": round(avg, 2)
    })


# ===========================
# ✏️ EDIT PARENT
# ===========================

@login_required
def edit_parent(request, id):

    parent = get_object_or_404(Parent, id=id)
    students = Student.objects.all()

    if request.method == "POST":
        student_id = request.POST.get("student")

        if student_id:
            parent.student = Student.objects.get(id=student_id)
            parent.save()
            messages.success(request, "Parent updated successfully")

        return redirect("parent_home")

    return render(request, "hod_template/edit_parent.html", {
        "parent": parent,
        "students": students
    })


# ===========================
# ❌ DELETE PARENT
# ===========================

@login_required
def delete_parent(request, id):

    parent = get_object_or_404(Parent, id=id)

    parent.admin.delete()  # supprime user + parent auto
    messages.success(request, "Parent deleted successfully")

    return redirect("parent_home")


# ===========================
# 🔥 FIREBASE (UNCHANGED)
# ===========================

def showFirebaseJS(request):
    data = """
    importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-app.js');
    importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-messaging.js');

    firebase.initializeApp({
        apiKey: "xxx",
        authDomain: "xxx",
        databaseURL: "xxx",
        projectId: "xxx",
        storageBucket: "xxx",
        messagingSenderId: "xxx",
        appId: "xxx"
    });

    const messaging = firebase.messaging();
    """
    return HttpResponse(data, content_type='application/javascript')

