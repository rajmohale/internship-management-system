from django.db import migrations


def backfill_snapshots(apps, schema_editor):
    Application = apps.get_model("internship_app", "Application")
    for app in Application.objects.select_related("internship").all():
        internship = app.internship
        if not app.company_name_snapshot:
            app.company_name_snapshot = internship.company_name or internship.title
        if not app.domain_snapshot:
            app.domain_snapshot = internship.domain or "Not specified"
        if not app.internship_mode_snapshot and internship.internship_mode:
            app.internship_mode_snapshot = internship.internship_mode
        if not app.stipend_type_snapshot and internship.stipend_type:
            app.stipend_type_snapshot = internship.stipend_type
        if app.stipend_amount_snapshot is None and internship.stipend_amount is not None:
            app.stipend_amount_snapshot = internship.stipend_amount
        if app.start_date_snapshot is None and internship.start_date is not None:
            app.start_date_snapshot = internship.start_date
        if app.end_date_snapshot is None and internship.end_date is not None:
            app.end_date_snapshot = internship.end_date
        app.save()


class Migration(migrations.Migration):
    dependencies = [
        ("internship_app", "0006_application_company_name_snapshot_and_more"),
    ]

    operations = [
        migrations.RunPython(backfill_snapshots, migrations.RunPython.noop),
    ]

