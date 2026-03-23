from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.utils import timezone

from .models import Internship, Application
from permission_app.models import PermissionRequest
from notification_app.models import Notification
from users.models import CustomUser



def _build_dashboard_rows(request):
    applications = Application.objects.select_related(
        "student",
        "internship",
    ).order_by("-applied_at")
    permissions = PermissionRequest.objects.select_related("student", "internship")

    if request.user.role == "faculty":
        applications = applications.filter(internship__faculty=request.user)
        permissions = permissions.filter(internship__faculty=request.user)
    elif request.user.role != "admin":
        return None, None, {}

    offer_letter_map = {
        (perm.student_id, perm.internship_id): perm for perm in permissions
    }

    # Filters
    has_offer_letter = request.GET.get("has_offer_letter", "")
    paid_status = request.GET.get("paid_status", "")
    mode = request.GET.get("mode", "")
    department = request.GET.get("department", "")
    domain = request.GET.get("domain", "")

    if paid_status in ("paid", "unpaid"):
        applications = applications.filter(internship__stipend_type=paid_status)
    if mode in ("online", "offline", "hybrid"):
        applications = applications.filter(internship__internship_mode=mode)
    if department:
        applications = applications.filter(student__branch__iexact=department)
    if domain:
        applications = applications.filter(internship__domain__iexact=domain)

    rows = []
    for app in applications:
        permission = offer_letter_map.get((app.student_id, app.internship_id))
        has_offer = bool(permission and permission.offer_letter)
        if has_offer_letter == "yes" and not has_offer:
            continue
        if has_offer_letter == "no" and has_offer:
            continue

        industry_value = (
            app.company_name_snapshot
            or app.internship.company_name
            or app.internship.title
        )
        domain_value = (
            app.domain_snapshot
            or app.internship.domain
            or "Not specified"
        )
        mode_value = app.internship_mode_snapshot or app.internship.internship_mode
        stipend_type_value = app.stipend_type_snapshot or app.internship.stipend_type
        stipend_amount_value = (
            app.stipend_amount_snapshot
            if app.stipend_amount_snapshot is not None
            else app.internship.stipend_amount
        )
        start_date_value = app.start_date_snapshot or app.internship.start_date
        end_date_value = app.end_date_snapshot or app.internship.end_date
        department_value = app.student.branch or app.student.student_class or "Not specified"

        rows.append(
            {
                "application": app,
                "student": app.student,
                "internship": app.internship,
                "permission": permission,
                "has_offer_letter": has_offer,
                "industry_value": industry_value,
                "domain_value": domain_value,
                "mode_value": mode_value,
                "stipend_type_value": stipend_type_value,
                "stipend_amount_value": stipend_amount_value,
                "start_date_value": start_date_value,
                "end_date_value": end_date_value,
                "department_value": department_value,
            }
        )

    filter_options = {
        "departments": list(
            CustomUser.objects.filter(role="student")
            .exclude(branch__isnull=True)
            .exclude(branch__exact="")
            .order_by("branch")
            .values_list("branch", flat=True)
            .distinct()
        ),
        "domains": list(
            Internship.objects.exclude(domain__isnull=True)
            .exclude(domain__exact="")
            .order_by("domain")
            .values_list("domain", flat=True)
            .distinct()
        ),
    }

    selected_filters = {
        "has_offer_letter": has_offer_letter,
        "paid_status": paid_status,
        "mode": mode,
        "department": department,
        "domain": domain,
    }
    return rows, filter_options, selected_filters

@login_required
def admin_dashboard(request):
    if request.user.role != "admin":
        return redirect("home")
    rows, filter_options, selected_filters = _build_dashboard_rows(request)
    context = {
        "dashboard_title": "Admin Dashboard",
        "table_rows": rows,
        "offer_letter_rows": [row for row in rows if row["has_offer_letter"]],
        "filter_options": filter_options,
        "selected_filters": selected_filters,
    }
    return render(request, "internship_app/management_dashboard.html", context)
# ==========================
# FACULTY DASHBOARD
# ==========================
@login_required
def faculty_dashboard(request):
    if request.user.role != "faculty":
        return redirect("home")
    rows, filter_options, selected_filters = _build_dashboard_rows(request)
    context = {
        "dashboard_title": "Faculty Dashboard",
        "table_rows": rows,
        "offer_letter_rows": [row for row in rows if row["has_offer_letter"]],
        "filter_options": filter_options,
        "selected_filters": selected_filters,
    }
    return render(request, "internship_app/management_dashboard.html", context)


# ==========================
# STUDENT DASHBOARD
# ==========================
@login_required
def student_dashboard(request):

    if request.user.role != "student":
        return redirect("home")

    apps = Application.objects.filter(student=request.user)

    permissions = PermissionRequest.objects.filter(student=request.user)

    context = {

        "total_applied": apps.count(),

        "approved": permissions.filter(status="approved").count(),

        "pending": permissions.filter(
            Q(status="pending_faculty") |
            Q(status="pending_hod")
        ).count(),

        "completed": permissions.filter(status="completed").count(),

        "rejected": permissions.filter(status="rejected").count()

    }

    return render(
        request,
        "internship_app/student_dashboard.html",
        context
    )


# ==========================
# EXPORT APPLICATIONS CSV
# ==========================
@login_required
def export_applications_csv(request):

    if request.user.role != "faculty":
        return redirect("home")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=applications.csv"

    writer = csv.writer(response)

    writer.writerow([
        "Student Name",
        "Email",
        "Internship",
        "Status",
        "Applied Date"
    ])

    applications = Application.objects.filter(
        internship__faculty=request.user
    )

    for app in applications:
        writer.writerow([
            f"{app.student.first_name} {app.student.last_name}",
            app.student.email,
            app.internship.title,
            app.status,
            app.applied_at
        ])

    return response


# ==========================
# FACULTY: VIEW APPLICATIONS
# ==========================
@login_required
def faculty_applications(request):
    if request.user.role != "faculty":
        return redirect("home")

    applications = Application.objects.filter(
        internship__faculty=request.user
    ).select_related("student", "internship").order_by("-applied_at")

    # Search by student class
    search_class = request.GET.get("class", "")
    if search_class:
        applications = applications.filter(student__student_class=search_class)

    return render(
        request,
        "internship_app/faculty_applications.html",
        {"applications": applications, "search_class": search_class}
    )


# ==========================
# INTERNSHIP LIST + SEARCH
# ==========================
@login_required
def internship_list(request):

    query = request.GET.get("q")
    location = request.GET.get("location")
    faculty = request.GET.get("faculty")

    internships = Internship.objects.filter(status="OPEN")

    if query:
        internships = internships.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    if location:
        internships = internships.filter(
            location__icontains=location
        )

    if faculty:
        internships = internships.filter(
            faculty__first_name__icontains=faculty
        )

    return render(
        request,
        "internship_app/internship_list.html",
        {"internships": internships}
    )


# ==========================
# INTERNSHIP DETAIL
# ==========================
@login_required
def internship_detail(request, internship_id):

    internship = get_object_or_404(
        Internship,
        id=internship_id
    )

    return render(
        request,
        "internship_app/internship_detail.html",
        {"internship": internship}
    )


# ==========================
# APPLY INTERNSHIP
# ==========================
@login_required
def apply_internship(request, internship_id):

    if request.user.role != "student":
        return redirect("home")

    internship = get_object_or_404(
        Internship,
        id=internship_id
    )
    today = timezone.now().date()
    if internship.status != "OPEN" or internship.deadline < today:
        messages.error(request, "This internship is closed for new applications.")
        return redirect("internship_detail", internship_id=internship.id)

    if Application.objects.filter(
        student=request.user,
        internship=internship
    ).exists():

        messages.warning(
            request,
            "You have already applied for this internship."
        )

        return redirect(
            "internship_detail",
            internship_id=internship.id
        )

    if request.method == "POST":

        resume = request.FILES.get("resume")
        cover_letter = request.FILES.get("cover_letter")

        if not resume:

            messages.error(
                request,
                "Please upload your resume."
            )

            return redirect(
                "apply_internship",
                internship_id=internship.id
            )

        Application.objects.create(
            student=request.user,
            internship=internship,
            resume=resume,
            cover_letter=cover_letter,
            status="applied",
            company_name_snapshot=internship.company_name,
            domain_snapshot=internship.domain,
            internship_mode_snapshot=internship.internship_mode,
            stipend_type_snapshot=internship.stipend_type,
            stipend_amount_snapshot=internship.stipend_amount,
            start_date_snapshot=internship.start_date,
            end_date_snapshot=internship.end_date,
        )

        Notification.objects.create(
            user=internship.faculty,
            message=f"{request.user.first_name} applied for {internship.title}"
        )

        messages.success(
            request,
            "Application submitted successfully!"
        )

        return redirect("internship_list")

    return render(
        request,
        "internship_app/apply_internship.html",
        {"internship": internship}
    )


# ==========================
# ADD INTERNSHIP (FACULTY)
# ==========================
@login_required
def add_internship(request):

    if request.user.role != "faculty":
        return redirect("home")

    if request.method == "POST":

        title = request.POST.get("title")
        description = request.POST.get("description")
        duration = request.POST.get("duration")
        location = request.POST.get("location")
        deadline = request.POST.get("deadline")
        company_name = request.POST.get("company_name", "").strip()
        domain = request.POST.get("domain", "").strip()
        internship_mode = request.POST.get("internship_mode") or None
        stipend_type = request.POST.get("stipend_type") or None
        stipend_amount_raw = request.POST.get("stipend_amount", "").strip()
        start_date = request.POST.get("start_date") or None
        end_date = request.POST.get("end_date") or None
        stipend_amount = None

        if not title or not description or not deadline:

            messages.error(
                request,
                "Title, Description and Deadline are required."
            )

            return redirect("add_internship")

        if not company_name or not domain or not internship_mode or not stipend_type or not start_date or not end_date:
            messages.error(
                request,
                "Company, domain, mode, stipend type, start date, and end date are required."
            )
            return redirect("add_internship")

        try:
            deadline_dt = datetime.strptime(deadline, "%Y-%m-%d").date()
            start_date_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Please provide valid dates.")
            return redirect("add_internship")

        today = timezone.now().date()
        if deadline_dt < today:
            messages.error(request, "Deadline cannot be in the past.")
            return redirect("add_internship")
        if start_date_dt > end_date_dt:
            messages.error(request, "Start date cannot be after end date.")
            return redirect("add_internship")
        if deadline_dt > start_date_dt:
            messages.error(request, "Application deadline should be on or before internship start date.")
            return redirect("add_internship")

        if stipend_type == "paid":
            if not stipend_amount_raw:
                messages.error(request, "Please enter stipend amount for paid internships.")
                return redirect("add_internship")
            try:
                stipend_amount = Decimal(stipend_amount_raw)
                if stipend_amount <= 0:
                    raise InvalidOperation
            except (InvalidOperation, ValueError):
                messages.error(request, "Stipend amount must be a valid positive number.")
                return redirect("add_internship")
        elif stipend_type == "unpaid":
            stipend_amount = None

        Internship.objects.create(

            faculty=request.user,
            title=title,
            description=description,
            duration=duration,
            location=location,
            deadline=deadline,
            company_name=company_name,
            domain=domain,
            internship_mode=internship_mode,
            stipend_type=stipend_type,
            stipend_amount=stipend_amount,
            start_date=start_date,
            end_date=end_date,
            status="OPEN"
        )

        messages.success(
            request,
            "Internship added successfully!"
        )

        return redirect("faculty_dashboard")

    return render(
        request,
        "internship_app/add_internship.html"
    )


# ==========================
# MY APPLICATIONS (STUDENT)
# ==========================
@login_required
def my_applications(request):

    if request.user.role != "student":
        return redirect("home")

    applications = Application.objects.filter(
        student=request.user
    )

    unread_notifications_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return render(
        request,
        "internship_app/my_applications.html",
        {
            "applications": applications,
            "unread_notifications_count": unread_notifications_count
        }
    )


# ==========================
# UPLOAD OFFER LETTER
# ==========================
@login_required
def upload_offer_letter(request):

    if request.user.role != "student":
        return redirect("home")

    if request.method == "POST":

        file = request.FILES.get("offer_letter")

        if not file:
            messages.error(request, "Please upload an offer letter.")
            return redirect("student_dashboard")

        permission = PermissionRequest.objects.create(

            student=request.user,
            offer_letter=file,
            status="pending_faculty"
        )

        faculties = CustomUser.objects.filter(role="faculty")

        for faculty in faculties:
            Notification.objects.create(
                user=faculty,
                message=f"{request.user.first_name} uploaded an offer letter."
            )

        messages.success(request, "Offer letter uploaded successfully.")

        return redirect("student_dashboard")

    return render(
        request, "internship_app/upload_offer_letter.html"
    )


@login_required
def export_dashboard_csv(request):
    if request.user.role not in ("admin", "faculty"):
        return redirect("home")

    rows, _, _ = _build_dashboard_rows(request)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="{request.user.role}_dashboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    )
    writer = csv.writer(response)
    writer.writerow(
        [
            "PRN",
            "Student Name",
            "Department",
            "Industry",
            "Domain",
            "Start Date",
            "End Date",
            "Offer Letter",
            "Internship Mode",
            "Paid/Unpaid",
            "Stipend Amount (INR)",
        ]
    )

    for row in rows:
        student = row["student"]
        internship = row["internship"]
        permission = row["permission"]
        writer.writerow(
            [
                student.prn or "NA",
                f"{student.first_name} {student.last_name}".strip(),
                row["department_value"],
                row["industry_value"],
                row["domain_value"],
                row["start_date_value"] or "Not specified",
                row["end_date_value"] or "Not specified",
                "Available" if row["has_offer_letter"] else "NA",
                dict(Internship._meta.get_field("internship_mode").choices).get(
                    row["mode_value"], "Not specified"
                ),
                dict(Internship._meta.get_field("stipend_type").choices).get(
                    row["stipend_type_value"], "Not specified"
                ),
                row["stipend_amount_value"] if row["stipend_amount_value"] is not None else "Not specified",
            ]
        )
    return response