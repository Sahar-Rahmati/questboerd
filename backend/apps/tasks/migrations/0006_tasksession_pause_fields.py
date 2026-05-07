from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0005_task_archive_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="tasksession",
            name="accumulated_seconds",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="tasksession",
            name="paused_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
