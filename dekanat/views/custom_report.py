import datetime
import json

from django.shortcuts import render

from dekanat.controllers.serialize_student import serialize_student
from dekanat.controllers.views_controllers import ViewGroup
from dekanat.models.group import Group
from dekanat.views.contingent import get_request_students
from print.file_response_utils import get_file_response
from print.print_reports.custom_report import CustomReportPrinter

default_fields = [{'name': 'full_name', 'label': 'Полное имя', 'header': 'ФИО', 'width': 10},
                  {'name': 'short_name', 'label': 'Сокращенное имя', 'header': 'ФИО', 'width': 10},
                  {'name': 'birthday', 'label': 'Дата рождения', 'width': 10},
                  {'name': 'citizen', 'label': 'Гражданство', 'width': 10},
                  {'name': 'gender', 'label': 'Пол', 'width': 10},
                  {'name': 'foreign_lang', 'label': 'Иностранный язык', 'width': 10},
                  {'name': 'phone', 'label': 'Телефон', 'width': 10},
                  {'name': 'reg_address', 'label': 'Адрес регистрации', 'width': 10},
                  {'name': 'fact_address', 'label': 'Адрес проживания', 'width': 10},
                  {'name': 'zcode', 'label': 'Номер зачетной книжки', 'width': 10},
                  {'name': 'tutor', 'label': 'Научный руководитель', 'width': 10},
                  {'name': 'diploma_theme', 'label': 'Тема работы', 'width': 10},
                  {'name': 'group', 'label': 'Группа', 'width': 10},
                  {'name': 'kaf', 'label': 'Выпускающая кафедра', 'width': 10},
                  {'name': 'institute', 'label': 'Институт', 'width': 10},
                  {'name': 'kurs', 'label': 'Курс', 'width': 10},
                  {'name': 'edu_form', 'label': 'Форма обучения', 'width': 10},
                  {'name': 'edu_type', 'label': 'Основа обучения', 'width': 10},
                  {'name': 'spec_code', 'label': 'Код направления', 'width': 10},
                  {'name': 'spec_name', 'label': 'Наименование направление', 'width': 10},
                  {'name': 'subspec_code', 'label': 'Код профиля', 'width': 10},
                  {'name': 'subspec_name', 'label': 'Наименование профиля', 'width': 10},
                  {'name': 'ent_doc_num', 'label': 'Номер приказа о зачислении', 'width': 10},
                  {'name': 'ent_doc_date', 'label': 'Дата приказа о зачислении', 'width': 10},
                  {'name': 'deduct_order_num', 'label': 'Номер приказа об отчислении', 'width': 10},
                  {'name': 'deduct_order_date', 'label': 'Дата приказа об отчислении', 'width': 10},
                  {'name': 'prev_edu_org', 'label': 'Организация пред. образования', 'width': 10},
                  {'name': 'prev_edu_end_year', 'label': 'Год окончания предыдущего образования', 'width': 10},
                  {'name': 'debt', 'label': 'Cумма долга', 'width': 10},
                  {'name': 'snils', 'label': 'СНИЛС', 'width': 10},
                  {'name': 'empty', 'label': 'Пустой', 'header': 'Подпись', 'width': 10}]


# View для создания отчета

def get_report_modal(request):
    return render(request, 'contingent/custom_report.html', dict(fields=default_fields))


def create_report_data(dep, students, params):
    """
    Возвращает данные для настраиваемого отчета
    :param dep: Подразделение в котором строится отчет
    :param students: Список студентов в отчете
    :param params: Список полей необходимых в отчете, а так же настройки страницы
    :return:
    """
    report_data = []
    fields = [field['name'] for field in params['fields']]
    for i, student in enumerate(students):
        student_data = serialize_student(student, fields)
        if params['print_number']:
            student_data['number'] = i + 1
        report_data.append(student_data)

    title_table = []
    if params['kurator'] and students:
        info_group = students[0].group.groupinfo_set.first()
        kurator = str(info_group.kurator) if info_group else ''
        title_table.append(['Куратор', kurator])

    if params['starosta'] and students:
        info_group = students[0].group.groupinfo_set.first()
        starosta = str(info_group.starosta) if info_group else ''
        title_table.append(['Староста', starosta])

    if params['print_date']:
        title_table.append(['Дата формирования отчета', datetime.datetime.now().strftime('%d.%m.%Y - %H:%M')])

    for brim in params['brims']:
        params['brims'][brim] = float(params['brims'][brim])

    list_size = 21 if params['is_portrait'] else 29.7  # размер a4

    if params['print_number']:
        list_size -= 1  # 1 см на столбец с номером

    # от ширины листа a4 отнимаем поля, чтобы получить размер таблицы
    list_size = list_size - params['brims']['left'] - params['brims']['right']
    # пересичтываем размер в процентах на размер в см
    for field in params['fields']:
        field['width'] = float(field['width']) / 100 * list_size

    if params['print_number']:
        params['fields'].insert(0, {'name': 'number', 'header': '№ п/п', 'width': 1})

    param_dict = {'title': params['title'],
                  'title_table': title_table,
                  'brims': params['brims'],
                  'fields': params['fields'],
                  'data': report_data,
                  'footer': params['footer'],
                  'is_sign': params['print_sign']}

    if params['print_sign'] and hasattr(dep, 'edudepartment'):
        settings = dep.edudepartment.get_settings()
        param_dict['type_chief'] = settings.head_post_name
        param_dict['chief'] = settings.head

    return param_dict


def create_report(request, dep_id, node_id=1, type=0, status=1, date=None):
    params = json.loads(request.GET.get('params'))
    students = get_request_students(request, dep_id, node_id, type, status, date)
    param_dict = create_report_data(request.curr_dep, students, params)
    crp = CustomReportPrinter('custom_report.pdf', param_dict, params['is_portrait'])
    crp.print()
    return get_file_response(request, crp.file_name, False)


def print_group_list(request, group_id):
    group = Group.objects.get(id=group_id)
    students = ViewGroup(group).get_all_student()
    params = dict(fields=[{'name': 'full_name', "header": "ФИО", "width": "70"},
                          {'name': 'edu_type', "header": "Основа обучения", "width": "30"}],
                  title=f'Список группы {str(group)}',
                  footer='',
                  starosta=True,
                  kurator=True,
                  print_date=False,
                  print_number=True,
                  print_sign=False,
                  is_portrait=True,
                  brims={"top": "1", "bottom": "1", "left": "2", "right": "1"}
                  )
    param_dict = create_report_data(request.curr_dep, students, params)
    crp = CustomReportPrinter('custom_report.pdf', param_dict, params['is_portrait'])
    crp.print()
    return get_file_response(request, crp.file_name, False)
