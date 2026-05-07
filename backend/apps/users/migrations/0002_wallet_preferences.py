from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="apple_pay_enabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="samsung_pay_enabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="wallet_card_brand",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="wallet_card_expiry_month",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="wallet_card_expiry_year",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="wallet_card_last4",
            field=models.CharField(blank=True, max_length=4),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="wallet_cardholder_name",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="wallet_permissions_granted",
            field=models.BooleanField(default=False),
        ),
    ]
