from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0004_tasksession"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="archived_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="task",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name="task",
            index=models.Index(fields=["user", "is_archived"], name="tasks_task_user_id_84ddc8_idx"),
        ),
    ]
