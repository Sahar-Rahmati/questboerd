import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0003_freeform_ai_category"),
    ]

    operations = [
        migrations.CreateModel(
            name="TaskSession",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("started_at", models.DateTimeField()),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                ("tracked_duration_minutes", models.PositiveIntegerField(default=0)),
                ("reward_blocked_reason", models.CharField(blank=True, max_length=255)),
                ("task", models.OneToOneField(on_delete=models.deletion.CASCADE, related_name="session", to="tasks.task")),
            ],
            options={
                "ordering": ["-started_at"],
            },
        ),
    ]
