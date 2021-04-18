# coding=utf-8
from enum import IntEnum

from django.db import models

from contingent.models import Group
from contingent.models.address import Address
from contingent.models.dict import DictCitizen, DictLang, DictEduType


class StudentInfo(models.Model):
    """
        Основая информация об обучающемся
    """
    birthday = models.DateField(u'Дата рождения', null=True, blank=True)

    class GenderChoice(IntEnum):
        MALE = 1
        FEMALE = 0

        @classmethod
        def choices(cls):
            return (1, 'мужской'), (0, 'женский')

    gender = models.IntegerField(u'Пол', choices=GenderChoice.choices(), null=True, blank=True)
    citizen = models.ForeignKey(DictCitizen, on_delete=models.SET_NULL, null=True, blank=True)
    foreign_lang = models.ForeignKey(DictLang, on_delete=models.SET_NULL, null=True, blank=True)
    phone_1c = models.CharField(u'Телефоны из 1С', max_length=50, null=True, blank=True)
    phone = models.CharField(u'Телефон', max_length=50, null=True, blank=True)

    email = models.EmailField(u'E-Mail', null=True, blank=True)
    fact_address = models.OneToOneField(Address, verbose_name=u'Фактический адрес проживания', null=True, blank=True,
                                        on_delete=models.SET_NULL)
    reg_address = models.OneToOneField(Address, verbose_name=u'Адрес регистрации', related_name='+', null=True,
                                       blank=True, on_delete=models.SET_NULL)
    family_status_all = ((0, 'неженат/незамужем'), (1, 'женат/замужем'))
    family_status = models.IntegerField(u'Семейное положение', choices=family_status_all, null=True, blank=True)
    is_orphan = models.BooleanField(u'Сирота', default=False, blank=True)
    is_invalid = models.BooleanField(u'Инвалид', default=False, blank=True)
    invalid_group = models.IntegerField(u'Группа инвалидности', null=True, blank=True)
    is_chernobyl = models.BooleanField(u'Чернобыль', default=False, blank=True)
    is_large_family = models.BooleanField('Из многодетной семьи', default=False, blank=True)
    children_count = models.PositiveSmallIntegerField('Количество детей', default=0)
    single_mother = models.BooleanField('Мать-одиночка', default=False, blank=True)
    photo = models.ImageField(upload_to='photo/', verbose_name='Фото', null=True, blank=True)

    payment_contract_number = models.CharField('Номер договора', max_length=100, null=True, blank=True)


class StudentJob(models.Model):
    """
        Сведения о трудоустройстве
    """
    name = models.CharField(u'Наименование предприятия', max_length=200, null=True, blank=True)
    addr = models.CharField(u'Адрес предприятия', max_length=500, null=True, blank=True)
    self = models.BooleanField(u'Самостоятельное трудоустройство', default=False, blank=True)
    cert = models.CharField(u'Удостоверение о трудоустройстве', max_length=500, null=True, blank=True)


class Student(models.Model):
    uid = models.CharField(u'Уникальный идентификатор человека', max_length=100, blank=True, null=True)
    name = models.CharField(u"Имя", max_length=256, null=True, blank=True)
    surname = models.CharField(u"Фамилия", max_length=256, null=True, blank=True)
    patronymic = models.CharField(u"Отчество", max_length=256, null=True, blank=True)
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

    info = models.OneToOneField(StudentInfo, on_delete=models.CASCADE, null=True, blank=True)
    job = models.OneToOneField(StudentJob, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if self.patronymic:
            return "{} {} {}".format(self.surname, self.name, self.patronymic)
        return "{} {}".format(self.surname, self.name)

    def delete(self, using=None, keep_parents=False):
        if self.info:
            if self.info.reg_address:
                self.info.reg_address.delete()
            if self.info.fact_address:
                self.info.fact_address.delete()
            self.info.delete()
        if self.job:
            self.job.delete()

    def short_name(self):
        """
        :return: ФИО студента с инициалами
        """
        name = "{} {}.".format(self.surname, self.name[0])
        if self.patronymic:
            name = name + ' {}.'.format(self.patronymic[0])
        return name

    class Meta:
        ordering = 'surname', 'name'
