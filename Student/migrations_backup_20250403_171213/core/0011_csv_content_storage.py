# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_csvinput_associated_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='csvinput',
            name='file',
        ),
        migrations.AddField(
            model_name='csvinput',
            name='csv_content',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csvinput',
            name='file_name',
            field=models.CharField(default='unnamed.csv', max_length=255),
            preserve_default=False,
        ),
    ]
