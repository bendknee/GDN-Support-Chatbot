# Generated by Django 2.0.5 on 2018-08-03 07:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hangouts', '0014_auto_20180803_0711'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreatedWorkItems',
            fields=[
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hangouts.User')),
            ],
        ),
    ]
