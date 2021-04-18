# -*- coding: utf-8 -*-
import json
from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from contingent.controllers.serialize_student import serialize_student
from contingent.controllers.students_filter import get_students_fields
from contingent.controllers.views_controllers import ViewDepartment, ViewSpec, ViewGroup
from contingent.models import Spec, Group, DictEduType, Student
from contingent.models.depart import Department


def get_filter_query(filter_info, value):
    filter_kwargs = dict()
    if filter_info['filter_type'] == 'select':
        if filter_info['json_field'] == 'mil_office' and value[0] == '-1':
            return ~Q(**{filter_info['db_field'] + '__in': [38, 37, 51, 50]}) & \
                   Q(**{filter_info['db_field'] + '__isnull': False})
        if filter_info['json_field'] == 'is_snils':
            if value[0] == '1':
                return Q(**{filter_info['db_field'] + '__isnull': False}) & ~Q(**{filter_info['db_field']: ''})
            elif value[0] == '0':
                return Q(**{filter_info['db_field'] + '__isnull': True}) | Q(
                    **{filter_info['db_field'] + '__exact': ''})
        if len(value) > 1:
            filter_kwargs[filter_info['db_field'] + '__in'] = value
        else:
            filter_kwargs[filter_info['db_field']] = value[0]
    elif filter_info['filter_type'] == 'bool':
        if filter_info['json_field'] in ('is_starosta', 'debt', 'is_snils'):
            filter_kwargs[filter_info['db_field']] = False
        else:
            filter_kwargs[filter_info['db_field']] = True
    elif filter_info['filter_type'] == 'date':
        period = value.split(' - ')
        if len(period) > 1:
            date_start = datetime.strptime(period[0], '%d.%m.%Y')
            date_end = datetime.strptime(period[1], '%d.%m.%Y')
            filter_kwargs[filter_info['db_field'] + '__gte'] = date_start
            filter_kwargs[filter_info['db_field'] + '__lte'] = date_end
        else:
            date = datetime.strptime(period[0], '%d.%m.%Y')
            filter_kwargs[filter_info['db_field']] = date
    elif filter_info['json_field'] == 'fact_address' or filter_info['json_field'] == 'reg_address':
        return Q() | \
               Q(**{filter_info['db_field'] + '__region': value}) | \
               Q(**{filter_info['db_field'] + '__district': value}) | \
               Q(**{filter_info['db_field'] + '__settlement': value}) | \
               Q(**{filter_info['db_field'] + '__street': value}) | \
               Q(**{filter_info['db_field'] + '__district': value})
    else:
        filter_kwargs[filter_info['db_field'] + '__icontains'] = value

    return Q(**filter_kwargs)


def get_students(dep_id, node_id, type=0, status=1, filter_fields=None, filter_params=()):
    q = Q()
    for param in filter_params:
        filter_info = next((item for item in filter_fields if item['json_field'] == param['name']), False)
        if not filter_info:
            return HttpResponseBadRequest('Имя фильтра {} не найдено'.format(param['name']))
        q = q & get_filter_query(filter_info, param['value'])
    institute = Department.objects.get(id=dep_id)
    if type == 0 or type == 1:  # "Department" или кафедра:
        dep = Department.objects.get(id=node_id)
        return ViewDepartment(dep).get_all_student(status, q)
    if type == 2:  # "Spec":
        spec = Spec.objects.get(id=node_id)
        return ViewSpec(spec, institute).get_all_student(status, q)
    if type == 3:  # "Group":
        group = Group.objects.get(id=node_id)
        return ViewGroup(group).get_all_student(status, q)
    if type == 8:  # "EduForm":
        return ViewDepartment(institute).get_all_student(status, q).filter(plan__spec__eduForm=node_id)


def get_students_table(dep_id, node_id, type, status, page=1, filter_fields=None, filter_params=()):
    students = get_students(dep_id, int(node_id), int(type), int(status), filter_fields, filter_params)
    students_pagination = Paginator(students, 30).get_page(page)
    students_dict = []
    fields = [field['json_field'] for field in get_students_fields() if 'json_field' in field]
    for student in students_pagination:
        students_dict.append(serialize_student(student, fields))
    return {'students': json.dumps(students_dict),
            'pagination': render_to_string('contingent/contingent_pagination.html',
                                           dict(pagination=students_pagination))}


def get_students_table_response(request, dep_id, node_id, type, status):
    filter_params = json.loads(request.GET.get('filter', '[]'))
    page = int(request.GET.get('page', '1'))
    filter_fields = get_students_fields(request.curr_dep)
    return JsonResponse(get_students_table(dep_id, node_id, type, status, page, filter_fields, filter_params))


def open_all_contingent(request):
    dep = request.curr_dep
    view_type = request.GET.get('viewtype', None)
    students_table = get_students_table(dep.id, dep.id, 0, 1, 1)
    edu_types = DictEduType.objects.all()
    return render(request, 'contingent/contingent.html',
                  dict(students_table=students_table, view_type=view_type, edu_types=edu_types,
                       fields=json.dumps(get_students_fields(dep))))


def get_students_by_date(dep_id, date, node_id, type=0, status=1, filter_fields=None, filter_params=()):
    q_hist = Q()
    q_no_hist = Q()
    for param in filter_params:
        filter_info = next((item for item in filter_fields if item['json_field'] == param['name']), False)
        if not filter_info:
            return HttpResponseBadRequest('Имя фильтра {} не найдено'.format(param['name']))
        q = get_filter_query(filter_info, param['value'])
        if filter_info.get('history', False):
            q_hist = q_hist & q
        else:
            q_no_hist = q_no_hist & q

    students = []
    institute = Department.objects.get(id=dep_id)
    if type == 0:  # "Department":
        dep = Department.objects.get(id=node_id)
        students.extend(ViewDepartment(dep).get_all_students_in_history(date, status, q_no_hist, q_hist))
    if type == 1:  # Kafedra
        kaff = Department.objects.get(id=node_id)
        students.extend(ViewDepartment(kaff).get_all_students_in_history(date, status, q_no_hist, q_hist))
    if type == 2:  # "Spec":
        spec = Spec.objects.get(id=node_id)
        students.extend(ViewSpec(spec, institute).get_all_students_in_history(date, status, q_no_hist, q_hist))
    if type == 3:  # "Group":
        group = Group.objects.get(id=node_id)
        students.extend(ViewGroup(group).get_all_students_in_history(date, status, q_no_hist, q_hist))
    if type == 8:  # "EduForm":
        q_hist = q_hist & Q(plan__spec__eduForm=node_id)
        return ViewDepartment(institute).get_all_students_in_history(date, status, q_no_hist, q_hist)
    return students


def get_students_table_by_date(dep_id, date, id, type, status, page, filter_fields=None, request_params=()):
    students = get_students_by_date(dep_id, date, int(id), int(type), int(status), filter_fields, request_params)
    students_pagination = Paginator(students, 30).get_page(page)
    students_dict = []
    fields = [field['json_field'] for field in get_students_fields() if 'json_field' in field]
    for student in students_pagination:
        student = get_student_state(student.student, student)  # fixme
        students_dict.append(serialize_student(student, fields))

    return {'students': json.dumps(students_dict),
            'pagination': render_to_string('contingent/contingent_pagination.html',
                                           dict(pagination=students_pagination))}


def get_students_table_by_date_response(request, date, dep_id, node_id, type, status):
    date = datetime.strptime(date, '%d.%m.%Y').date()
    request_params = json.loads(request.GET.get('filter', '[]'))
    page = int(request.GET.get('page', '1'))
    filter_fields = get_students_fields(request.curr_dep)
    return JsonResponse(
        get_students_table_by_date(dep_id, date, node_id, type, status, page, filter_fields, request_params))


def open_all_contingent_by_date(request, date):
    date = datetime.strptime(date, '%d.%m.%Y').date()
    dep = request.curr_dep
    view_type = request.GET.get('viewtype', None)
    students_table = get_students_table_by_date(dep.id, date, dep.id, type=0, status=1, page=1)
    return render(request, 'contingent/contingent.html',
                  dict(students_table=students_table, date=date, view_type=view_type,
                       fields=json.dumps(get_students_fields(dep))))


def get_request_students(request, dep_id, node_id, type, status, date):
    students = request.GET.getlist('students', [])

    if students and students[0]:
        return Student.objects.filter(id__in=students)

    request_params = json.loads(request.GET.get('filter', '[]'))
    filter_fields = get_students_fields(request.curr_dep)
    if date:
        date = datetime.strptime(date, '%d.%m.%Y').date()
        students = []
        hist_students = get_students_by_date(dep_id, date, int(node_id), int(type), int(status),
                                             filter_fields, request_params)
        for student in hist_students:
            student = get_student_state(student.student, student)  # fixme
            students.append(student)
        return students
    return get_students(dep_id, int(node_id), int(type), int(status), filter_fields, request_params)


def analitic(request):
    return render(request, 'analitics.html')
