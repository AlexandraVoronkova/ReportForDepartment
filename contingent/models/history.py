from django.db import models

from contingent.models import Group, DictEduType, Student


class StudentHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    # Статус
    StatusChoices = (
        (0, 'Абитуриент'),
        (1, 'Обучающийся'),
        (2, 'Выпускник'),
        (3, 'Отчисленный'),
        (4, 'В академическом отпуске'),
    )
    status = models.IntegerField(choices=StatusChoices, null=True, blank=True)

    # Данные об обучении
    edu_type = models.ForeignKey(DictEduType, on_delete=models.CASCADE, null=True, blank=True)
    zcode = models.CharField(u'Номер зачетной книжки', max_length=20, null=True, blank=True)

    kurs = models.IntegerField(default=1)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)

    date = models.DateField(auto_now=True)
    order_name = models.CharField(max_length=100, blank=True)
