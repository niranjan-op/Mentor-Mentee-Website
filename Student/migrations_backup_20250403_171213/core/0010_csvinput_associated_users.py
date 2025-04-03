# Generated manually
"""
Add associated_users field to CSVInput model
"""

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0009_merge_20250404_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='csvinput',
            name='associated_users',
            field=models.ManyToManyField(blank=True, related_name='source_csv_files', to=settings.AUTH_USER_MODEL),
        ),
    ]
