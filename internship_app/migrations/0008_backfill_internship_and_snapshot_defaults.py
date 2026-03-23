from django.db import migrations
from django.utils import timezone
from datetime import timedelta


def fill_missing_values(apps, schema_editor):
    Internship = apps.get_model("internship_app", "Internship")
    Application = apps.get_model("internship_app", "Application")

    today = timezone.now().date()

    for internship in Internship.objects.all():
        changed = False
        if not internship.company_name:
            internship.company_name = internship.title or "Industry TBD"
            changed = True
        if not internship.domain:
            internship.domain = "General"
            changed = True
        if not internship.internship_mode:
            internship.internship_mode = "offline"
            changed = True
        if not internship.stipend_type:
            internship.stipend_type = "unpaid"
            changed = True
        if internship.stipend_type == "unpaid" and internship.stipend_amount is None:
            internship.stipend_amount = 0
            changed = True
        if internship.start_date is None:
            internship.start_date = today
            changed = True
        if internship.end_date is None:
            internship.end_date = internship.start_date + timedelta(days=90)
            changed = True
        if internship.deadline and internship.start_date and internship.deadline > internship.start_date:
            internship.deadline = internship.start_date
            changed = True

        if changed:
            internship.save()

    for app in Application.objects.select_related("internship", "student").all():
        internship = app.internship
        changed = False

        if not app.company_name_snapshot:
            app.company_name_snapshot = internship.company_name or internship.title or "Industry TBD"
            changed = True
        if not app.domain_snapshot:
            app.domain_snapshot = internship.domain or "General"
            changed = True
        if not app.internship_mode_snapshot:
            app.internship_mode_snapshot = internship.internship_mode or "offline"
            changed = True
        if not app.stipend_type_snapshot:
            app.stipend_type_snapshot = internship.stipend_type or "unpaid"
            changed = True
        if app.stipend_amount_snapshot is None:
            app.stipend_amount_snapshot = internship.stipend_amount if internship.stipend_amount is not None else 0
            changed = True
        if app.start_date_snapshot is None:
            app.start_date_snapshot = internship.start_date or today
            changed = True
        if app.end_date_snapshot is None:
            app.end_date_snapshot = internship.end_date or (app.start_date_snapshot + timedelta(days=90))
            changed = True

        if changed:
            app.save()


class Migration(migrations.Migration):
    dependencies = [
        ("internship_app", "0007_backfill_application_snapshots"),
    ]

    operations = [
        migrations.RunPython(fill_missing_values, migrations.RunPython.noop),
    ]

