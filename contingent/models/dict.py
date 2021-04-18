# -*- coding: utf-8 -*-
from django.db import models


class DictCitizen(models.Model):
    """
        Справочник гражданств
    """
    citizen = models.CharField(max_length=100)
    smallname = models.CharField(max_length=20, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.citizen


class DictLang(models.Model):
    """
        Справочник иностранных языков
    """
    Langs = (
        (1, 'Английский'),
        (2, 'Немецкий'),
        (3, 'Французский'),
        (4, 'Испанский'),
        (5, 'Итальянский'),
        (6, 'Турецкий'),
        (7, 'Корейский'),
        (8, 'Арабский'),
        (9, 'Русский'),
        (10, 'Другой'),
    )
    lang = models.IntegerField(choices=Langs, null=True, blank=True)
    smallname = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.get_lang_display()


class DictEduForm(models.Model):
    """
        Справочник Форм обучения
    """
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class DictEduType(models.Model):
    """
        Справочник типов обучения
    """
    name = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name


class DictStipendType(models.Model):
    """
        Справочник видов стипендий
    """
    BASE = 0
    FIRST_COURSE = 1
    SESSION_ONLY_4 = 2
    SESSION_4_AND_5 = 3
    SESSION_ONLY_5 = 4
    EDU_ACHIEVEMENT = 5
    SCIENCE_ACHIEVEMENT = 6
    OTHER_ACHIEVEMENT = 7

    STIPEND_TYPES = ((BASE, 'Базовая стипендия'),
                     (FIRST_COURSE, 'Первый курс первый семестр'),
                     (SESSION_ONLY_4, 'Обучающиеся на хорошо'),
                     (SESSION_4_AND_5, 'Обучающиеся на хорошо и отлично'),
                     (SESSION_ONLY_5, 'Обучающиеся на отлично'),
                     (EDU_ACHIEVEMENT, 'За достижения в учебной деятельности'),
                     (SCIENCE_ACHIEVEMENT, 'За достижения в научной деятельности'),
                     (OTHER_ACHIEVEMENT, 'За достижения в общ., культ. или спорт. деятельности'))

    type = models.IntegerField(choices=STIPEND_TYPES, default=0)
    percent = models.IntegerField('Процент от базовой', null=True, blank=True)
    amount = models.IntegerField('Сумма стипендии')
    code = models.IntegerField(u'Код для бухгалтерии', null=True, blank=True)

    def save(self, *args, **kwargs):
        self.amount = 2000 * self.percent / 100
        super().save(*args, **kwargs)

    def __str__(self):
        return '{}({})'.format(self.get_type_display(), self.level)


class DictPrevEduLevel(models.Model):
    """
        Справочник уровней предыдущего образования
    """
    PrevEduLevels = (
        (1, 'Среднее специальное'),
        (2, 'Среднее общее'),
        (3, 'Среднее профессиональное'),
        (4, 'Начальное профессиональное'),
    )
    prevEduLevel = models.IntegerField(choices=PrevEduLevels, null=True, blank=True)

    def __str__(self):
        return self.get_prevEduLevel_display()


class DictReasonDeductStudent(models.Model):
    REASON_TYPE = (
        (1, 'По неуспеваемости'),
        (2, 'По собственному желанию'),
        (3, 'Переводом в другой вуз'),
        (4, 'Из академ. отпуска'),
        (5, 'В связи с просрочкой оплаты'),
        (6, 'По причине смерти'),
        (7, 'По болезни'),
        (8, 'В связи с не прохождением итоговой аттестации'),
        (9, 'В связи с призывом в ряды вооруженных сил'),
        (10, 'Не приступившего к занятиям'),
        (11, 'Другая причина'),
        (12, 'Отчислить условно переведенного'),
    )
    reason = models.IntegerField(choices=REASON_TYPE, null=True, blank=True)

    @staticmethod
    def init_dict():
        for reason in DictReasonDeductStudent.REASON_TYPE:
            try:
                r = DictReasonDeductStudent.objects.get(reason=reason[0])
            except ObjectDoesNotExist:
                DictReasonDeductStudent(reason=reason[0]).save()

    def __str__(self):
        return self.get_reason_display()


class Spec(models.Model):
    """
        Справочник специальностей
    """
    name = models.CharField(u'Наименование', max_length=300)
    code = models.CharField(u'Код', max_length=50, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    default_group_name = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return '{} {}'.format(self.code, self.name)
