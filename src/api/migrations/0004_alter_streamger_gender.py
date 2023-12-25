# Generated by Django 5.0 on 2023-12-25 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_streamger_gender_alter_streamger_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='streamger',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1, null=True),
        ),
    ]
