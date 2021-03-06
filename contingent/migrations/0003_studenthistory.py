# Generated by Django 3.2 on 2021-04-18 01:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contingent', '0002_auto_20210418_0433'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(blank=True, choices=[(0, 'Абитуриент'), (1, 'Обучающийся'), (2, 'Выпускник'), (3, 'Отчисленный'), (4, 'В академическом отпуске')], null=True)),
                ('zcode', models.CharField(blank=True, max_length=20, null=True, verbose_name='Номер зачетной книжки')),
                ('kurs', models.IntegerField(default=1)),
                ('date', models.DateField(auto_now=True)),
                ('order_name', models.CharField(blank=True, max_length=100)),
                ('edu_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contingent.dictedutype')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contingent.group')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contingent.student')),
            ],
        ),
    ]
