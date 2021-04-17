# coding=utf-8
from enum import IntEnum

from django.db import models

from dekanat.models.group import Group
from dict_app.models_.address import Address
from dict_app.models_.depart import EduDepartment
from dict_app.models_.dict import DictCitizen, DictLang, DictDocType, DictEduType, \
    DictRelativeDegree, DictVKRType, DictEduDocType, DictPrevEduLevel, \
    DictPrevEduDocType, DictAchievType, DictMilOffice, DictTypeOrder, DictStudPersDepDocType
from dict_app.models_.employer import EmployerInfo, Department
from edu_plans.models import Plan, PlanSubject


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


class StudentAbitInfo(models.Model):
    """
        Данные, полученные при зачислении от приемной комиссии
    """
    id_1c = models.CharField(u'Идентификатор обучающегося в 1C-Университет', max_length=20, null=True, blank=True)
    abit_is_direction = models.BooleanField(u'Целевой набор', default=False, blank=True)
    abit_edu_form = models.CharField(u'Форма обучения', max_length=30, null=True, blank=True)
    abit_spec_code = models.CharField(u'Код направления/специальности', max_length=30, null=True, blank=True)
    abit_spec_name = models.CharField(u'Наименование направления/специальности', max_length=200, null=True, blank=True)
    abit_subspec_code = models.CharField(u'Код профиля/специализации/направленности', max_length=30, null=True,
                                         blank=True)
    abit_subspec_name = models.CharField(u'Наименование профиля/специализации/направленности', max_length=200,
                                         null=True, blank=True)
    abit_with_spo = models.BooleanField(u'Абитуриент со средним профессиональным образованием', default=False,
                                        blank=True)
    # Номер и дата приказа о зачислении

    ent_doc_num = models.CharField(u'Номер приказа о зачислении', max_length=20, null=True, blank=True)
    ent_doc_date = models.DateField(u'Дата приказа о зачислении', null=True, blank=True)

    abit_dep = models.ForeignKey(EduDepartment, on_delete=models.CASCADE, verbose_name='Подразделение', null=True,
                                 blank=True)

    """
        Данные, заполняемые при зачислении из другого ВУЗа
    """
    another_type = models.BooleanField(u'Он с другого ВУЗа? ', default=False, blank=True, null=True)
    another_doc_type_choice = ((0, 'справка об обучении'), (1, 'академическая справка'))
    another_doc_type = models.IntegerField(u'Предыдущий документ', choices=another_doc_type_choice, null=True,
                                           blank=True)
    another_doc_series = models.CharField(u'Серия', max_length=10, null=True, blank=True)
    another_doc_number = models.CharField(u'Номер', max_length=20, null=True, blank=True)
    another_year_start = models.IntegerField(u'Год поступления в предыдущий ВУЗ', null=True, blank=True)
    another_name = models.CharField(u'Наименование ВУЗа, из которого поступил студент', max_length=500, null=True,
                                    blank=True)


class StudentPrevEdu(models.Model):
    """
        Данные о предыдущем образовании
    """
    prevEduLevel = models.ForeignKey(DictPrevEduLevel, on_delete=models.CASCADE, null=True, blank=True)
    prevEduOrg = models.CharField(u'Организация, выдавшая документ об образовании', max_length=2000, null=True,
                                  blank=True)
    yearEnd = models.IntegerField(u'Год окончания предыдущего образования', null=True, blank=True)
    prevEduDocType = models.ForeignKey(DictPrevEduDocType, on_delete=models.CASCADE, null=True, blank=True)
    prevEduDocSer = models.CharField(u'Серия документа о предыдущем образовании', max_length=1000, null=True,
                                     blank=True)
    prevEduDocNum = models.CharField(u'Номер документа о предыдущем образовании', max_length=1000, null=True,
                                     blank=True)
    is_prev_edu_orginal = models.BooleanField(u'Оригинал', blank=True, null=True)
    prevEduDocDateGet = models.DateField(u'Дата получения документа о предыдущем образовании', max_length=1000,
                                         null=True, blank=True)
    prevEduDocCountry = models.CharField(u'Страна, выдавшая документ о предыдущем образовании', max_length=1000,
                                         null=True, blank=True)
    prevEduSpec = models.CharField(u'Специальность, полученная в предыдущем образовании', max_length=1000, null=True,
                                   blank=True)

    def get_doc_name(self):
        try:
            prepositional = " ".join([word[:-1] + "м" for word in str(self.prevEduLevel).split()])
            return f'{str(self.prevEduDocType)} о {prepositional} ' \
                   f'образовании, выданный в {self.prevEduDocDateGet.year} году'.lower()
        except AttributeError:
            return 'НЕ ЗАПОЛНЕНО'

    def get_small_doc_name(self):
        try:
            if self.prevEduDocType.prevEduDocType == 1:
                number_doc = f'ат. {self.prevEduDocSer} {self.prevEduDocNum}'
            elif self.prevEduDocType.prevEduDocType in range(2, 8):
                number_doc = f'дип. {self.prevEduDocSer} {self.prevEduDocNum}'
            else:
                number_doc = 'нет'
        except:
            number_doc = 'нет'
        return number_doc


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
        (5, 'Обучающийся с продленной защитой'),
        (6, 'Состояние для межфакультетских перемещений'),
        (7, 'Переведенный на повторный курс со старого ДЕКАНАТА'),
        (8, 'Переведенный на старший курс в старый ДЕКАНАТ'),
    )
    status = models.IntegerField(choices=StatusChoices, null=True, blank=True)

    # Данные об обучении
    edu_type = models.ForeignKey(DictEduType, on_delete=models.CASCADE, null=True, blank=True)
    zcode = models.CharField(u'Номер зачетной книжки', max_length=20, null=True, blank=True)

    kurs = models.IntegerField(default=1)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)

    # Руководитель и тема ВКР
    diploma_tutor = models.ForeignKey(EmployerInfo, on_delete=models.CASCADE, null=True, blank=True)
    diploma_theme = models.CharField(u'Тема ВКР', max_length=1000, null=True, blank=True)

    info = models.OneToOneField(StudentInfo, on_delete=models.CASCADE, null=True, blank=True)
    prev_edu = models.OneToOneField(StudentPrevEdu, on_delete=models.CASCADE, null=True, blank=True)
    job = models.OneToOneField(StudentJob, on_delete=models.CASCADE, null=True, blank=True)
    abit_info = models.OneToOneField(StudentAbitInfo, on_delete=models.CASCADE, null=True, blank=True)

    facultative_subjects = models.ManyToManyField(PlanSubject, blank=True, related_name='+')
    elective_subjects = models.ManyToManyField(PlanSubject, blank=True, related_name='+')

    exclude_learn_subjects = models.ManyToManyField(PlanSubject, blank=True)

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
        if self.person_doc:
            self.person_doc.delete()
        if self.docs:
            self.docs.delete()
        if self.bank_details:
            self.bank_details.delete()
        if self.prev_edu:
            self.prev_edu.delete()
        if self.hostel:
            self.hostel.delete()
        if self.mil_info:
            self.mil_info.delete()
        if self.job:
            self.job.delete()
        if self.abit_info:
            self.abit_info.delete()
        if self.debt:
            self.debt.delete()
        if self.health_check:
            self.health_check.delete()

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


class StudentFIOCase(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    GENITIVE = 0
    DATIVE = 1
    case = models.IntegerField(choices=(('Родительный', GENITIVE), ('Дательный', DATIVE)))
    name = models.CharField(u"Имя", max_length=256)
    surname = models.CharField(u"Фамилия", max_length=256)
    patronymic = models.CharField(u"Отчество", max_length=256, blank=True)


class DocStudPersDep(models.Model):
    """
    Документы для студенческого отдела кадров
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    series = models.CharField(u'Серия', max_length=1000, null=True, blank=True)
    number = models.CharField(u'Номер', max_length=1000, null=True, blank=True)
    type_doc = models.ForeignKey(DictStudPersDepDocType, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    sign = models.BooleanField(u'Оригинал', blank=True, null=True)
    # Статус
    StatusChoices = (
        (0, 'На руках'),
        (1, 'В подразделении'),
        (2, 'В личном деле'),
        (3, 'Утерян')
    )
    status = models.IntegerField(u'Статус', choices=StatusChoices, null=True, blank=True)
    doc_date = models.DateField(u'Дата изменения', auto_now=True)

    def __str__(self):
        return f'Серия: {self.series} Номер: {self.number} {type}'


class OtherDocStudPersDep(models.Model):
    """
    Другие документы для студенческого отдела кадров
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    edu_books = models.BooleanField(u'Учебные книги', default=True, blank=True)
    student_card = models.BooleanField(u'Студенческий билет', default=True, blank=True)
    workaround_page = models.BooleanField(u'Обходной лист', default=True, blank=True)
    exam_book = models.BooleanField(u'Зачётная книжка', default=True, blank=True)

    def __str__(self):
        doc_name = list()
        if self.edu_books:
            doc_name.append('учеб. кн')
        if self.student_card:
            doc_name.append('студ. билет')
        if self.workaround_page:
            doc_name.append('обх. лист')
        if self.exam_book:
            doc_name.append('зач. кн.')
        return ", ".join(doc_name)
