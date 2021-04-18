# coding=utf-8
from django.db import models

from contingent.models.depart import Department
from contingent.models.dict import Spec


class Group(models.Model):
    name_group = models.CharField(u'Название группы', max_length=100, null=True, blank=True)
    kurs = models.IntegerField(u'Курс', null=True, blank=True, default=1)
    spec_group = models.ForeignKey(Spec, on_delete=models.SET_NULL, null=True, blank=True)
    created_year = models.IntegerField(u'Год создания группы', null=True, blank=True, default=2000)
    created_date_group = models.DateField(u'Дата создания', null=True, blank=True)
    free_date_group = models.DateField(u'Дата расформирования группы', null=True, blank=True)

    dep = models.ForeignKey(Department, on_delete=models.SET_NULL,
                            verbose_name='подразделение', null=True, blank=True)

    def __str__(self):
        return self.name_group

    class Meta:
        ordering = '-created_year', 'name_group'
