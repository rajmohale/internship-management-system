from django.urls import path
from . import views

urlpatterns = [

    # Internship list
    path('', views.internship_list, name='internship_list'),

    # Internship detail
    path('detail/<int:internship_id>/', views.internship_detail, name='internship_detail'),

    # Apply internship
    path('apply/<int:internship_id>/', views.apply_internship, name='apply_internship'),

    # Add internship
    path('add/', views.add_internship, name='add_internship'),

    # My applications
    path('my-applications/', views.my_applications, name='my_applications'),

    # Faculty: view applications for internships
    path('applications/', views.faculty_applications, name='faculty_applications'),

    # CSV export
    path('export-csv/', views.export_applications_csv, name='export_applications_csv'),
]