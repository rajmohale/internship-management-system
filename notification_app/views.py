from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Notification
from permission_app.models import PermissionRequest

# ---------------------------------------
# Notification Views
# ---------------------------------------
@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Compute unread count
    unread_notifications_count = notifications.filter(is_read=False).count()
    
    return render(request, 'notification_app/notifications.html', {
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    })

@login_required
def mark_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications_list')


# ---------------------------------------
# Permission Review (Faculty)
# ---------------------------------------
def is_faculty(user):
    return user.is_authenticated and user.role == 'faculty'

@login_required
@user_passes_test(is_faculty)
def review_permission(request, permission_id):
    permission = get_object_or_404(
        PermissionRequest, 
        id=permission_id, 
        internship__faculty=request.user
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            permission.status = 'approved'
            permission.save()
            Notification.objects.create(
                user=permission.student,
                message=f"Your offer letter for {permission.internship.title} has been approved!"
            )
            messages.success(request, "Offer letter approved.")
        elif action == 'reject':
            permission.status = 'rejected'
            permission.save()
            Notification.objects.create(
                user=permission.student,
                message=f"Your offer letter for {permission.internship.title} has been rejected."
            )
            messages.success(request, "Offer letter rejected.")

        return redirect('faculty_dashboard')

    return render(request, 'permission_app/review_permission.html', {'permission': permission})


from notification_app.models import Notification


def get_notifications(user):

    notifications = Notification.objects.filter(
        user=user
    ).order_by("-created_at")[:5]

    count = Notification.objects.filter(
        user=user,
        is_read=False
    ).count()

    return notifications, count    