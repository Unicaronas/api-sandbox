# Generated by Django 2.1.7 on 2019-04-02 20:30

import django.core.validators
from django.db import migrations, models
import user_data.models


class Migration(migrations.Migration):

    dependencies = [
        ('user_data', '0009_auto_20190402_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentproof',
            name='proof_scan_url',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='studentproof',
            name='proof',
            field=models.FileField(upload_to=user_data.models.filename, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'png'])]),
        ),
    ]