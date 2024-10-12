# Generated by Django 5.1.2 on 2024-10-12 08:18

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('WebAdmin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='tbl_services',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assignboat_starttime', models.TimeField(default=datetime.time(0, 0))),
                ('duration', models.DurationField(blank=True, null=True)),
                ('rate', models.FloatField(default=0.0)),
                ('status', models.IntegerField(default=1)),
                ('assignboat_boat', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='WebAdmin.tbl_boat')),
                ('services_endpoint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services_endpoints', to='WebAdmin.tbl_place')),
                ('services_startpoint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services_startpoints', to='WebAdmin.tbl_place')),
            ],
        ),
    ]
