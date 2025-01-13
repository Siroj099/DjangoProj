# Generated by Django 5.1.4 on 2025-01-10 07:09

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangoApp', '0004_remove_comment_djangoapp_c_comment_5f66a7_idx'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='ticket',
            name='djangoApp_t_title_28a501_idx',
        ),
        migrations.AlterField(
            model_name='comment',
            name='date',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='date',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='title',
            field=models.CharField(db_index=True, max_length=80),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['date'], name='djangoApp_c_date_3711b5_idx'),
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['title'], name='djangoApp_t_title_dd1775_idx'),
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['description'], name='djangoApp_t_descrip_fbfd46_idx'),
        ),
    ]