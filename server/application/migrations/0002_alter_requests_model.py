# Generated by Django 5.1.3 on 2024-12-15 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("application", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="requests",
            name="model",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
