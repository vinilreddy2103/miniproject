# Generated by Django 5.1.6 on 2025-02-08 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='habit',
            old_name='count',
            new_name='current_count',
        ),
        migrations.AddField(
            model_name='habit',
            name='target_count',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
