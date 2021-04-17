from django.db.models import F

from dekanat.controllers.views_controllers import ViewDepartment
from dekanat.models.student import StudentMilitaryControl
from dict_app.models_.depart import EduDepartment
from dict_app.models_.dict import DictEduType, DictLang, DictEduForm, DictPrevEduLevel, DictLevels, DictMilOffice
from edu_plans.models.spec import Spec


def get_students_fields(dep=None):
    mil_office_options = [{'label': mil_of.name, 'value': mil_of.id} for mil_of in
                          DictMilOffice.objects.filter(id__in=[38, 37, 51, 50])]
    mil_office_options.append({'label': 'остальные', 'value': -1})
    if dep:
        students = ViewDepartment(dep).get_student_query_set()
        citizen_options = list(students
                               .filter(info__citizen__isnull=False)
                               .values(label=F('info__citizen__citizen'), value=F('info__citizen'))
                               .order_by('info__citizen')
                               .distinct('info__citizen'))
        specs_id = students.values_list('group__spec_group', flat=True)
        spec_code_options = [{'label': spec.code(), 'value': spec.id} for spec in Spec.objects.filter(id__in=specs_id)]
        subspecs_id = students.values_list('plan__spec', flat=True)
        subspec_code_options = [{'label': spec.code(), 'value': spec.id} for spec in
                                Spec.objects.filter(id__in=subspecs_id)]
        kurs_options = list(students
                            .values(label=F('group__kurs'), value=F('group__kurs'))
                            .order_by('group__kurs')
                            .distinct('group__kurs'))
    else:
        citizen_options = []
        spec_code_options = [{'label': spec.code(), 'value': spec.id} for spec in Spec.objects.all()]
        subspec_code_options = [{'label': spec.code(), 'value': spec.id} for spec in
                                Spec.objects.filter(spec__parent__isnull=False)]
        kurs_options = []
    fields_info = [
        {
            'label': 'Фамилия',
            'db_field': 'surname',
            'json_field': 'surname',
            'filter_type': 'text',
            'history': True
        },
        {
            'label': 'Имя',
            'db_field': 'name',
            'json_field': 'name',
            'filter_type': 'text',
            'history': True
        },
        {
            'label': 'Отчество',
            'db_field': 'patronymic',
            'json_field': 'patronymic',
            'filter_type': 'text',
            'history': True
        },
        {
            'label': 'Номер зачетной книжки',
            'db_field': 'zcode',
            'json_field': 'zcode',
            'filter_type': 'text',
            'history': True
        },
        {
            'label': 'Основа обучения',
            'db_field': 'edu_type',
            'json_field': 'edu_type',
            'filter_type': 'select',
            'options': [{'label': edu_type.get_edu_type_display(), 'value': edu_type.id}
                        for edu_type in DictEduType.objects.all()],
            'history': True
        },
        {
            'label': 'Группа',
            'db_field': 'group__name_group',
            'json_field': 'group',
            'filter_type': 'text',
            'history': True
        },
        {
            'label': 'Дата рождения',
            'db_field': 'info__birthday',
            'json_field': 'birthday',
            'filter_type': 'date',
            'history': False
        },
        {
            'label': 'Пол',
            'db_field': 'info__gender',
            'json_field': 'gender',
            'filter_type': 'select',
            'options': [{'label': 'мужской', 'value': 1}, {'label': 'женский', 'value': 0}],
            'hidden': True,
            'history': False
        },
        {
            'label': 'Гражданство',
            'db_field': 'info__citizen',
            'json_field': 'citizen',
            'filter_type': 'select',
            'options': citizen_options,
            'hidden': True,
            'history': False
        },
        {
            'label': 'Иностранный язык',
            'db_field': 'info__foreign_lang',
            'json_field': 'foreign_lang',
            'filter_type': 'select',
            'options': [{'label': lang.get_lang_display(), 'value': lang.id}
                        for lang in DictLang.objects.all()],
            'hidden': True,
            'history': False
        },
        {
            'label': 'Адрес регистрации',
            'db_field': 'info__reg_address',
            'json_field': 'reg_address',
            'filter_type': 'text',
            'hidden': True,
            'history': False
        },
        {
            'label': 'Адрес проживания',
            'db_field': 'info__fact_address',
            'json_field': 'fact_address',
            'filter_type': 'text',
            'hidden': True,
            'history': False
        },
        {
            'label': 'Телефон',
            'db_field': 'info__phone',
            'json_field': 'phone',
            'filter_type': 'text',
            'hidden': True,
            'history': False
        },
        {
            'label': 'Инвалид',
            'db_field': 'info__is_invalid',
            'json_field': 'is_invalid',
            'filter_type': 'bool',
            'hidden': True,
            'history': False
        },
        {
            'label': 'Многодетная семья',
            'db_field': 'info__is_large_family',
            'json_field': 'is_large_family',
            'filter_type': 'bool',
            'hidden': True,
            'history': False
        },
        {
            'label': 'Количество детей',
            'db_field': 'info__children_count',
            'json_field': 'children_count',
            'filter_type': 'select',
            'options': [{'label': '1', 'value': '1'}, {'label': '2', 'value': '2'}, {'label': '3', 'value': '3'}, ],
            'hidden': True,
            'history': False
        },
        {
            'label': 'Сирота',
            'db_field': 'info__is_orphan',
            'json_field': 'is_orphan',
            'filter_type': 'bool',
            'hidden': True,
            'history': False
        },
        {
            'label': 'Чернобылец',
            'db_field': 'info__is_chernobyl',
            'json_field': 'is_chernobyl',
            'filter_type': 'bool',
            'hidden': True,
            'history': False
        },
        {
            'label': 'Староста',
            'db_field': 'starosta__isnull',
            'json_field': 'is_starosta',
            'filter_type': 'bool',
            'hidden': True,
            'history': False
        },
        {
            'label': 'Номер приказа о зачислении',
            'db_field': 'abit_info__ent_doc_num',
            'json_field': 'ent_doc_num',
            'filter_type': 'text',
            'hidden': True,
            'history': False
        },
        {
            'label': 'Дата приказа о зачислении',
            'db_field': 'abit_info__ent_doc_date',
            'json_field': 'ent_doc_date',
            'filter_type': 'date',
            'hidden': True,
            'history': False
        },
        {
            'label': 'Целевой набор',
            'db_field': 'abit_info__abit_is_direction',
            'json_field': 'is_direction',
            'filter_type': 'bool',
            'hidden': True,
            'history': False
        },
        {
            'label': 'Курс',
            'db_field': 'group__kurs',
            'json_field': 'kurs',
            'filter_type': 'select',
            'options': kurs_options,
            'hidden': True,
            'history': True
        },
        {
            'label': 'Уровень образования',
            'db_field': 'group__spec_group__spec__level',
            'json_field': 'level',
            'filter_type': 'select',
            'options': [{'label': str(level), 'value': level.id}
                        for level in DictLevels.objects.all().order_by('level')],
            'hidden': True,
            'history': True
        },
        {
            'label': 'Код направления',
            'db_field': 'group__spec_group',
            'json_field': 'spec_code',
            'filter_type': 'select',
            'options': spec_code_options,
            'hidden': True,
            'history': True
        },
        {
            'label': 'Наименование направления',
            'db_field': 'group__spec_group__spec__name',
            'json_field': 'spec_name',
            'filter_type': 'text',
            'hidden': True,
            'history': True
        },
        {
            'label': 'Код профиля',
            'db_field': 'plan__spec',
            'json_field': 'subspec_code',
            'filter_type': 'select',
            'options': subspec_code_options,
            'hidden': True,
            'history': True
        },
        {
            'label': 'Наименование профиля',
            'db_field': 'plan__spec__spec__name',
            'json_field': 'subspec_name',
            'filter_type': 'text',
            'hidden': True,
            'history': True
        },
        {
            'label': 'Форма обучения',
            'db_field': 'group__spec_group__eduForm',
            'json_field': 'edu_form',
            'filter_type': 'select',
            'options': [{'label': edu_form.get_edu_form_display(), 'value': edu_form.id}
                        for edu_form in DictEduForm.objects.all()],
            'hidden': True,
            'history': True
        },
        {
            'label': 'Военно обязан',
            'db_field': 'mil_info__is_mil_reg',
            'json_field': 'is_mil_reg',
            'filter_type': 'select',
            'options': [{'label': 'да', 'value': 1}, {'label': 'нет', 'value': 0}],
            'hidden': True
        },
        {
            'label': 'Категория студента ',
            'db_field': 'mil_info__category',
            'json_field': 'category',
            'filter_type': 'select',
            'options': [{'label': category[1], 'value': category[0]} for category in
                        StudentMilitaryControl.mil_categories],
            'hidden': True
        },
        {
            'label': 'Военкомат',
            'db_field': 'mil_info__mil_office',
            'json_field': 'mil_office',
            'filter_type': 'select',
            'options': mil_office_options,
            'hidden': True
        },
        {
            'label': 'Учится на военной кафедре',
            'db_field': 'mil_info__is_mil_kaf',
            'json_field': 'is_mil_kaf',
            'filter_type': 'select',
            'options': [{'label': 'да', 'value': 1}, {'label': 'нет', 'value': 0}],
            'hidden': True
        },
        {
            'label': 'Учебная программа военной кафедры',
            'db_field': 'mil_info__mil_kaf_edu_program',
            'json_field': 'mil_kaf_edu_program',
            'filter_type': 'select',
            'options': [{'label': program[1], 'value': program[0]} for program in
                        StudentMilitaryControl.mil_kaf_edu_programes],
            'hidden': True
        },
        {
            'label': 'Уровень предыдущего образования',
            'db_field': 'prev_edu__prevEduLevel',
            'json_field': 'prev_edu_level',
            'filter_type': 'select',
            'options': [{'label': str(prev_edu), 'value': prev_edu.id}
                        for prev_edu in DictPrevEduLevel.objects.all()],
            'hidden': True
        },
        {
            'label': 'Дата флюорографии',
            'db_field': 'health_check__fluoro_last_date',
            'json_field': 'last_fluoru_date',
            'filter_type': 'date',
            'hidden': True
        },
        {
            'label': 'Номер договора на оплату',
            'db_field': 'info__payment_contract_number',
            'json_field': 'payment_contract_number',
            'filter_type': 'text',
            'hidden': True
        },
        {
            'label': 'Долг по оплате',
            'db_field': 'debt__isnull',
            'json_field': 'debt',
            'filter_type': 'bool',
            'hidden': True
        },
        {
            'label': 'Приказы по студенту',
            'db_field': '',
            'json_field': 'orders',
            'filter_type': 'text',
            'hidden': True
        },
        {
            'label': 'номер СНИЛС',
            'db_field': 'docs__snils_number',
            'json_field': 'snils',
            'filter_type': 'text',
            'hidden': True
        },
        {
            'label': 'указан СНИЛС',
            'db_field': 'docs__snils_number',
            'json_field': 'is_snils',
            'filter_type': 'select',
            'options': [{'label': 'да', 'value': 1}, {'label': 'нет', 'value': 0}],
            'hidden': True
        },
        {
            'label': 'Год окончания предыдущего образования',
            'db_field': 'prev_edu__prevEduDocDateGet__year',
            'json_field': 'prev_edu_end_year',
            'filter_type': 'text',
            'hidden': True
        },
        {
            'label': 'Место предыдущего образования',
            'db_field': 'prev_edu__prevEduOrg',
            'json_field': 'prev_edu_org',
            'filter_type': 'text',
            'hidden': True
        },
        {
            'label': 'Номер приказа об отчислении',
            'db_field': 'pointorderdeduct__order__name',
            'json_field': 'deduct_order_num',
            'filter_type': 'text',
            'hidden': True
        },
        {
            'label': 'Дата приказа об отчислении',
            'db_field': 'pointorderdeduct__order__date',
            'json_field': 'deduct_order_date',
            'filter_type': 'date',
            'hidden': True
        },
    ]
    if not dep or hasattr(dep, 'university'):
        fields_info.append({
            'label': 'Институт',
            'db_field': 'group__dep__dep',
            'json_field': 'institute',
            'filter_type': 'select',
            'options': [{'label': i.smallname, 'value': i.id}
                        for i in EduDepartment.objects.filter(type=1)],
            'hidden': True
        })
    return fields_info
