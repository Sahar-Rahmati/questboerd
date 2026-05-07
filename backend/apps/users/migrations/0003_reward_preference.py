from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_wallet_preferences"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="reward_preference",
            field=models.CharField(
                choices=[
                    ("bookstore", "Bookstore"),
                    ("study_cafe", "Study Cafe"),
                    ("gym_pool", "Gym / Pool"),
                ],
                default="bookstore",
                max_length=30,
            ),
        ),
    ]
