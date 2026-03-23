from django.urls import path
from . import views

urlpatterns = [
    path('submit-offer-letter/<int:internship_id>/', views.submit_offer_letter, name='submit_offer_letter'),
    path('my-requests/', views.permission_list_student, name='permission_list_student'),
    path('pending/', views.pending_approvals, name='pending_approvals'),
    path('approve/<int:request_id>/', views.approve_request, name='approve_request'),
    path('reject/<int:request_id>/', views.reject_request, name='reject_request'),
    path('submit-completion/<int:request_id>/', views.submit_completion, name='submit_completion'),
]