from .models import Notification

def unread_notifications(request):
    """
    Add unread notifications count and latest 5 notifications to all templates.
    """
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        latest_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        return {
            'unread_notifications_count': unread_count,
            'latest_notifications': latest_notifications,
        }
    return {
        'unread_notifications_count': 0,
        'latest_notifications': [],
    }