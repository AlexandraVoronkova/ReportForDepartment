# coding=utf-8
from django.db import models

from dict_app.models_.depart import EduDepartment
from dict_app.models_.dict import DictEduForm
from edu_plans.models import Spec


class Group(models.Model):
    name_group = models.CharField(u'Название группы', max_length=100, null=True, blank=True)
    edu_form = models.ForeignKey(DictEduForm, on_delete=models.SET_NULL, null=True, blank=True)
    kurs = models.IntegerField(u'Курс', null=True, blank=True, default=1)
    spec_group = models.ForeignKey(Spec, on_delete=models.SET_NULL, null=True, blank=True)
    created_year = models.IntegerField(u'Год создания группы', null=True, blank=True, default=2000)
    created_date_group = models.DateField(u'Дата создания', null=True, blank=True)
    free_date_group = models.DateField(u'Дата расформирования группы', null=True, blank=True)
    dep = models.ForeignKey(EduDepartment, on_delete=models.SET_NULL,
                            verbose_name='Выпускающая кафедра,РИМЦ или институт', null=True, blank=True)

    def get_course(self, edu_year):
        return edu_year.start - self.created_year + 1

    def get_institute(self):
        if self.dep.type == 1:
            return self.dep
        else:
            return self.dep.dep

    def __str__(self):
        return self.name_group

    class Meta:
        ordering = '-created_year', 'name_group'
