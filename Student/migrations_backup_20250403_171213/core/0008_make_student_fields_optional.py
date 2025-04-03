# Generated manually

from django.db import migrations, models
import django.db.models.deletion
import core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_remove_csvinput_original_filename_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='address',
            field=models.TextField(blank=True, help_text='Enter your full address', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='core.branch'),
        ),
        migrations.AlterField(
            model_name='student',
            name='division',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='core.division'),
        ),
        migrations.AlterField(
            model_name='student',
            name='dob',
            field=models.DateField(blank=True, help_text='Enter your date of birth in the format YYYY-MM-DD', null=True, validators=[core.validators.validate_dob]),
        ),
        migrations.AlterField(
            model_name='student',
            name='mentor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='core.mentor'),
        ),
        migrations.AlterField(
            model_name='student',
            name='phone_no_father',
            field=models.CharField(blank=True, help_text="Enter your father's phone number", max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='phone_no_mother',
            field=models.CharField(blank=True, help_text="Enter your mother's phone number", max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='phone_no_student',
            field=models.CharField(blank=True, help_text='Enter your phone number', max_length=12, null=True),
        ),
    ]
