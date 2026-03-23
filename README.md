# Internship Management System (IMS)

A full-stack Django web application for managing internships, student applications, offer letters, and permissions. Built with **Django** (backend), **Bootstrap 5**, **HTML/CSS/JS** (frontend).

## Features

- **Role-based Access**: Students, Faculty, Admin
- **Student**: Browse internships, apply, upload offer letters, track permissions, submit completion certificates
- **Faculty**: Post internships, approve students & offer letters, view applications, export CSV
- **Admin**: Dashboard analytics, approve faculty, manage offer letter approvals
- **Notifications**: Real-time notification system for approvals and updates
- **Modern UI**: Bootstrap 5, responsive design, charts (Chart.js)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Use email as username when prompted.

### 4. Run Development Server

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

## User Flow

1. **Register** → Choose role (Student/Faculty/Admin) → Wait for approval
2. **Login** → Redirected to role-specific dashboard
3. **Students**: Browse → Apply → Upload Offer Letter → Get Permission → Complete Internship
4. **Faculty**: Add Internships → Approve Students → Approve Offer Letters
5. **Admin**: Approve Faculty → Approve Offer Letters (HOD level)

## Project Structure

```
ims/
├── users/           # Auth, registration, profile
├── internship_app/  # Internships, applications
├── permission_app/  # Offer letters, permissions
├── notification_app/# Notifications
├── templates/       # Base template, dashboard
└── static/          # CSS, JS, images
```

## Tech Stack

- **Backend**: Django 5.x
- **Frontend**: Bootstrap 5, Bootstrap Icons, Chart.js
- **Database**: SQLite (default)
