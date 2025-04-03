# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_csvinput_mentors'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='current_semester',
            field=models.PositiveIntegerField(blank=True, choices=[(1, 'Semester 1'), (2, 'Semester 2'), (3, 'Semester 3'), (4, 'Semester 4'), (5, 'Semester 5'), (6, 'Semester 6'), (7, 'Semester 7'), (8, 'Semester 8')], help_text='Current semester of the student', null=True),
        ),
    ]
