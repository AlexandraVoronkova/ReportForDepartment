# -*- coding: utf-8 -*-
from datetime import datetime

from django.shortcuts import render

from contingent.models import Student


def get_int_from_request(request, field_name):
    if request.POST.get(field_name) == "":
        return None
    return int(request.POST.get(field_name))


def get_float_from_request(request, field_name):
    if request.POST.get(field_name) == "":
        return None
    return float(request.POST.get(field_name))


def get_char_from_request(request, field_name):
    if request.POST.get(field_name) == "":
        return None
    return request.POST.get(field_name)


def get_date_from_requests(request, field_date_name):
    date_str = request.POST.get(field_date_name)
    if date_str == '' or date_str == None:
        return None
    date_return = datetime.strptime(date_str, "%d.%m.%Y").date()
    return date_return


def openPageStudent(request, id_student):
    student = Student.objects.get(id=id_student)
    all_history_student = student.studenthistory_set.all().values('order', 'date')
    all_history_student = list(all_history_student)

    all_history_student = sorted(all_history_student, key=lambda x: x['date'])

    return render(request, "student_info/student.html",
                  dict(student=student, all_history_student=all_history_student, ))
