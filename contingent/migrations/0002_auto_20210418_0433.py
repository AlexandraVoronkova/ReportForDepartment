# Generated by Django 3.2 on 2021-04-18 01:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contingent', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Подразделение')),
                ('smallname', models.CharField(blank=True, max_length=200, null=True, verbose_name='Сокр. наименование')),
                ('dep', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contingent.department')),
            ],
        ),
        migrations.AddField(
            model_name='group',
            name='dep',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contingent.department', verbose_name='подразделение'),
        ),
    ]
