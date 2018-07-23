# Generated by Django 2.0.5 on 2018-07-23 07:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('state', models.CharField(default='initial', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='VstsArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('hangoutsSpaces', models.ManyToManyField(to='hangouts.User')),
            ],
        ),
        migrations.CreateModel(
            name='WorkItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='HardwareSupport',
            fields=[
                ('workitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='hangouts.WorkItem')),
                ('hardware_type', models.CharField(max_length=30)),
            ],
            bases=('hangouts.workitem',),
        ),
        migrations.CreateModel(
            name='SoftwareSupport',
            fields=[
                ('workitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='hangouts.WorkItem')),
                ('requested_by', models.CharField(max_length=30)),
                ('third_party', models.CharField(max_length=30)),
            ],
            bases=('hangouts.workitem',),
        ),
        migrations.AddField(
            model_name='user',
            name='work_item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='hangouts.WorkItem'),
        ),
    ]
