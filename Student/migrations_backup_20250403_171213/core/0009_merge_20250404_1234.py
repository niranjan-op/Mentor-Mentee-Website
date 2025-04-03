# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    """
    This migration merges two conflicting migration branches:
    - 0008_alter_csvinput_file
    - 0008_make_student_fields_optional
    """

    dependencies = [
        ('core', '0008_alter_csvinput_file'),
        ('core', '0008_make_student_fields_optional'),
    ]

    operations = [
        # No operations needed, this migration just merges the branches
    ]
