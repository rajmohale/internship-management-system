from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from internship_app.models import Internship
from notification_app.models import Notification
from .models import PermissionRequest
from .forms import OfferLetterForm, CompletionForm
from users.models import CustomUser


# ---------------- STUDENT: SUBMIT OFFER LETTER ----------------
@login_required
def submit_offer_letter(request, internship_id):

    if request.user.role != "student":
        return redirect("home")

    internship = get_object_or_404(Internship, id=internship_id)

    # Prevent duplicate submission
    if PermissionRequest.objects.filter(student=request.user, internship=internship).exists():
        messages.warning(request, "You have already submitted an offer letter for this internship.")
        return redirect("permission_list_student")

    if request.method == "POST":

        form = OfferLetterForm(request.POST, request.FILES)

        if form.is_valid():

            permission = form.save(commit=False)
            permission.student = request.user
            permission.internship = internship
            permission.status = "pending_faculty"
            permission.save()

            # Notify faculty
            Notification.objects.create(
                user=internship.faculty,
                message=f"{request.user.first_name} submitted an offer letter for {internship.title}."
            )

            messages.success(request, "Offer letter submitted successfully.")
            return redirect("permission_list_student")

    else:
        form = OfferLetterForm()

    return render(
        request,
        "permission_app/offer_letter_submit.html",
        {"form": form, "internship": internship}
    )


# ---------------- STUDENT: VIEW SUBMISSIONS ----------------
@login_required
def permission_list_student(request):

    if request.user.role != "student":
        return redirect("home")

    permissions = PermissionRequest.objects.filter(student=request.user)

    return render(
        request,
        "permission_app/student_permission_list.html",
        {"permissions": permissions}
    )


# ---------------- FACULTY & ADMIN: VIEW PENDING APPROVALS ----------------
@login_required
def pending_approvals(request):
    # Faculty sees requests waiting for faculty approval
    if request.user.role == "faculty":
        requests = PermissionRequest.objects.filter(
            status="pending_faculty",
            internship__faculty=request.user
        )
    # Admin acts as HOD
    elif request.user.role == "admin":
        requests = PermissionRequest.objects.filter(status="pending_hod")
    else:
        return redirect("home")

    # Search by student class
    search_class = request.GET.get("class", "")
    if search_class:
        requests = requests.filter(student__student_class=search_class)

    return render(
        request,
        "permission_app/pending_approvals.html",
        {"requests": requests, "search_class": search_class}
    )


# ---------------- APPROVE REQUEST ----------------
@login_required
def approve_request(request, request_id):
    if request.method != "POST":
        return redirect("pending_approvals")

    perm = get_object_or_404(PermissionRequest, id=request_id)

    # ---------- FACULTY APPROVAL ----------
    if request.user.role == "faculty" and perm.status == "pending_faculty":

        if perm.internship.faculty != request.user:
            messages.error(request, "You are not authorized to approve this request.")
            return redirect("pending_approvals")

        perm.status = "pending_hod"
        perm.save()

        # Notify student
        Notification.objects.create(
            user=perm.student,
            message=f"Faculty approved your offer letter for {perm.internship.title}. Awaiting admin approval."
        )

        # Notify admin users
        admins = CustomUser.objects.filter(role="admin")

        for admin in admins:
            Notification.objects.create(
                user=admin,
                message=f"Offer letter from {perm.student.first_name} requires approval."
            )

        messages.success(request, "Offer letter approved and forwarded to admin.")


    # ---------- ADMIN APPROVAL ----------
    elif request.user.role == "admin" and perm.status == "pending_hod":

        perm.status = "approved"
        perm.save()

        Notification.objects.create(
            user=perm.student,
            message=f"Your offer letter for {perm.internship.title} has been approved. You may start your internship."
        )

        messages.success(request, "Internship approved successfully.")

    else:
        messages.error(request, "Invalid approval action.")

    return redirect("pending_approvals")


# ---------------- REJECT REQUEST ----------------
@login_required
def reject_request(request, request_id):
    if request.method != "POST":
        return redirect("pending_approvals")

    perm = get_object_or_404(PermissionRequest, id=request_id)

    # ---------- FACULTY REJECTION ----------
    if request.user.role == "faculty" and perm.status == "pending_faculty":

        if perm.internship.faculty != request.user:
            messages.error(request, "You are not authorized to reject this request.")
            return redirect("pending_approvals")

        perm.status = "rejected"
        perm.save()

        Notification.objects.create(
            user=perm.student,
            message=f"Your offer letter for {perm.internship.title} was rejected by faculty."
        )

        messages.error(request, "Offer letter rejected.")


    # ---------- ADMIN REJECTION ----------
    elif request.user.role == "admin" and perm.status == "pending_hod":

        perm.status = "rejected"
        perm.save()

        Notification.objects.create(
            user=perm.student,
            message=f"Your offer letter for {perm.internship.title} was rejected by admin."
        )

        messages.error(request, "Offer letter rejected.")

    else:
        messages.error(request, "Invalid rejection action.")

    return redirect("pending_approvals")


# ---------------- STUDENT: SUBMIT COMPLETION ----------------
@login_required
def submit_completion(request, request_id):

    perm = get_object_or_404(PermissionRequest, id=request_id)

    # Only the student who owns the request
    if request.user != perm.student:
        return redirect("home")

    # Only after internship approval
    if perm.status != "approved":
        messages.error(request, "You can upload completion only after internship approval.")
        return redirect("permission_list_student")

    if request.method == "POST":

        form = CompletionForm(request.POST, request.FILES, instance=perm)

        if form.is_valid():

            completion = form.save(commit=False)
            completion.status = "completed"
            completion.save()

            # Notify faculty
            Notification.objects.create(
                user=perm.internship.faculty,
                message=f"{perm.student.first_name} has completed the internship: {perm.internship.title}."
            )

            messages.success(request, "Completion certificate uploaded successfully.")
            return redirect("permission_list_student")

    else:
        form = CompletionForm(instance=perm)

    return render(
        request,
        "permission_app/submit_completion.html",
        {
            "form": form,
            "permission": perm
        }
    )