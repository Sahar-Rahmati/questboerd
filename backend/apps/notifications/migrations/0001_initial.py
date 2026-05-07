from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tasks", "0003_freeform_ai_category"),
    ]

    operations = [
        migrations.CreateModel(
            name="PushSubscription",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("endpoint", models.TextField(unique=True)),
                ("p256dh_key", models.TextField()),
                ("auth_key", models.TextField()),
                ("expiration_time", models.BigIntegerField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("last_seen_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="push_subscriptions", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="TaskReminder",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("reminder_type", models.CharField(choices=[("exact_start", "Exact Start")], default="exact_start", max_length=30)),
                ("scheduled_for", models.DateTimeField()),
                ("sent_at", models.DateTimeField(auto_now_add=True)),
                ("delivery_count", models.PositiveIntegerField(default=0)),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("task", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reminders", to="tasks.task")),
            ],
            options={
                "ordering": ["-sent_at"],
            },
        ),
        migrations.AddIndex(
            model_name="pushsubscription",
            index=models.Index(fields=["user", "is_active"], name="notificatio_user_id_4c78f0_idx"),
        ),
        migrations.AddIndex(
            model_name="taskreminder",
            index=models.Index(fields=["scheduled_for"], name="notificatio_schedul_098ddd_idx"),
        ),
        migrations.AddConstraint(
            model_name="taskreminder",
            constraint=models.UniqueConstraint(fields=("task", "reminder_type"), name="unique_task_reminder_type"),
        ),
    ]
