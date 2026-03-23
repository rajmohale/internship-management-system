from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import (
    StudentRegistrationForm,
    FacultyRegistrationForm,
    AdminRegistrationForm,
    EmailAuthenticationForm
)

from .models import CustomUser
from notification_app.models import Notification


from .forms import ProfileUpdateForm


@login_required
def profile_view(request):

    return render(
        request,
        "users/profile.html",
        {"user": request.user}
    )


@login_required
def profile_edit(request):

    if request.method == "POST":

        form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile updated successfully!"
            )

            return redirect("profile")

    else:

        form = ProfileUpdateForm(
            instance=request.user
        )

    return render(
        request,
        "users/edit_profile.html",
        {"form": form}
    )


# ---------------- HOME ----------------
def home(request):
    """Redirect user to their dashboard based on role."""

    if request.user.is_authenticated:

        if request.user.role == "student":
            return redirect("student_dashboard")

        elif request.user.role == "faculty":
            return redirect("faculty_dashboard")

        elif request.user.role == "hod":
            return redirect("admin_dashboard")

        elif request.user.role == "admin":
            return redirect("admin_dashboard")

    return redirect("login")


# ---------------- REGISTER ----------------
def register(request):

    role = request.GET.get("role", "student")

    if request.method == "POST":

        role = request.POST.get("role")

        form_class = {
            "student": StudentRegistrationForm,
            "faculty": FacultyRegistrationForm,
            "admin": AdminRegistrationForm,
        }.get(role, StudentRegistrationForm)

        form = form_class(request.POST, request.FILES)

        if form.is_valid():

            user = form.save(commit=False)

            user.role = role
            user.status = "pending"
            user.is_active = False

            if role == "student":
                user.approval_stage = "faculty"

            user.save()

            # ---------------- NOTIFICATIONS ----------------

            # If student registers → notify faculty
            if role == "student":

                faculties = CustomUser.objects.filter(role="faculty")

                for faculty in faculties:
                    Notification.objects.create(
                        user=faculty,
                        message=f"New student registration pending approval: {user.first_name} {user.last_name}"
                    )

            # If faculty registers → notify admin
            elif role == "faculty":

                admins = CustomUser.objects.filter(role="admin")

                for admin in admins:
                    Notification.objects.create(
                        user=admin,
                        message=f"New faculty registration pending approval: {user.first_name} {user.last_name}"
                    )

            return render(
                request,
                "users/registration_pending.html",
                {"role": role}
            )

    else:

        form_class = {
            "student": StudentRegistrationForm,
            "faculty": FacultyRegistrationForm,
            "admin": AdminRegistrationForm,
        }.get(role, StudentRegistrationForm)

        form = form_class()

    return render(
        request,
        "users/register.html",
        {"form": form, "role": role}
    )


# ---------------- LOGIN ----------------
def user_login(request):

    if request.user.is_authenticated:
        return redirect("home")

    form = EmailAuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():

        email = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        user = authenticate(request, username=email, password=password)

        if user:

            if user.is_active and user.status == "active":

                login(request, user)
                return redirect("home")

            elif user.status == "pending":
                messages.warning(request, "Your account is pending approval.")

            elif user.status == "rejected":
                messages.error(request, "Your account was rejected. Contact admin.")

        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "users/login.html", {"form": form})


# ---------------- LOGOUT ----------------
@login_required
def user_logout(request):

    logout(request)
    return redirect("login")


# ---------------- PENDING STUDENTS ----------------
@login_required
def pending_students(request):
    if request.user.role not in ("faculty", "admin"):
        return redirect("home")

    students = CustomUser.objects.filter(
        role="student",
        status="pending",
        approval_stage="faculty"
    )

    # Search by class
    search_class = request.GET.get("class", "")
    if search_class:
        students = students.filter(student_class=search_class)

    return render(
        request,
        "users/pending_students.html",
        {"students": students, "search_class": search_class}
    )


# ---------------- APPROVE STUDENT ----------------
@login_required
def approve_student(request, student_id):
    if request.user.role not in ("faculty", "admin"):
        return redirect("home")
    if request.method != "POST":
        return redirect("pending_students")

    student = get_object_or_404(CustomUser, id=student_id, role="student")

    student.status = "active"
    student.is_active = True
    student.save()

    Notification.objects.create(
        user=student,
        message="Your registration has been approved by faculty. You can now login."
    )

    messages.success(request, f"{student.first_name} approved successfully.")

    return redirect("pending_students")


# ---------------- REJECT STUDENT ----------------
@login_required
def reject_student(request, student_id):
    if request.user.role not in ("faculty", "admin"):
        return redirect("home")
    if request.method != "POST":
        return redirect("pending_students")

    student = get_object_or_404(CustomUser, id=student_id, role="student")

    student.status = "rejected"
    student.is_active = False
    student.save()

    Notification.objects.create(
        user=student,
        message="Your account was rejected by faculty."
    )

    messages.error(request, f"{student.first_name} rejected.")

    return redirect("pending_students")


# ---------------- PENDING FACULTY ----------------
@login_required
def pending_faculty(request):

    if request.user.role != "admin":
        return redirect("home")

    faculty_list = CustomUser.objects.filter(
        role="faculty",
        status="pending"
    )

    return render(
        request,
        "users/pending_faculty.html",
        {"faculty_list": faculty_list}
    )


# ---------------- APPROVE FACULTY ----------------
@login_required
def approve_faculty(request, faculty_id):
    if request.user.role != "admin":
        return redirect("home")
    if request.method != "POST":
        return redirect("pending_faculty")

    faculty = get_object_or_404(CustomUser, id=faculty_id, role="faculty")

    faculty.status = "active"
    faculty.is_active = True
    faculty.save()

    Notification.objects.create(
        user=faculty,
        message="Your faculty account has been approved by admin."
    )

    messages.success(request, f"{faculty.first_name} approved successfully.")

    return redirect("pending_faculty")


# ---------------- REJECT FACULTY ----------------
@login_required
def reject_faculty(request, faculty_id):
    if request.user.role != "admin":
        return redirect("home")
    if request.method != "POST":
        return redirect("pending_faculty")

    faculty = get_object_or_404(CustomUser, id=faculty_id, role="faculty")

    faculty.status = "rejected"
    faculty.is_active = False
    faculty.save()

    Notification.objects.create(
        user=faculty,
        message="Your faculty account was rejected by admin."
    )

    messages.error(request, f"{faculty.first_name} rejected.")

    return redirect("pending_faculty")


# ---------------- DASHBOARDS ----------------
@login_required
def student_dashboard(request):
    return render(request, "dashboard.html", {"role": "student"})


@login_required
def faculty_dashboard(request):
    return render(request, "dashboard.html", {"role": "faculty"})


@login_required
def hod_dashboard(request):
    return render(request, "dashboard.html", {"role": "hod"})


@login_required
def admin_dashboard(request):
    return render(request, "dashboard.html", {"role": "admin"})