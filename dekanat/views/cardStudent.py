# -*- coding: utf-8 -*-
import json
from copy import copy
from datetime import datetime

from django.db.models import F
from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from dekanat.controllers.markbook import get_student_subjects_debts
from dekanat.controllers.tree_utils import get_tree
from dekanat.controllers.utils import update_address
from dekanat.forms.student import HostelForm, AnotherVuzDocForm
from dekanat.models.stipend import StudentStipend
from dekanat.models.student import Student,  StudentBankDetails, StudentInfo, DictCitizen, DictLang, \
    Address, StudentMilitaryControl, StudentPersonDoc, DictDocType, StudentRelative, DictRelativeDegree, \
    StudentPrevEdu, StudentHistoryOrder, HealthCheck, StudentHealth, StudentHostel, DocStudPersDep, OtherDocStudPersDep
from dict_app.models_.depart import EduDepartment, Department
from dict_app.models_.dict import DictMilOffice, DictPrevEduLevel, DictPrevEduDocType, DictTypeOrder, \
    DictStudPersDepDocType
from history_app.controllers.student_controller import get_all_points_student_history
from orders.models import PointOrderEnrollOtherVuz, Order, PointOrderDeductStudent


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


def get_health_info_student(student):
    health_info = student.health_check
    list_check = []
    all_health_check = HealthCheck.objects.filter(health_check=health_info).order_by("check_date")
    for check in all_health_check:
        list_check.append(check)
    return health_info, list_check


def openPageStudent(request, id_student):
    student = Student.objects.get(id=id_student)
    relatives = StudentRelative.objects.filter(student=student)
    isOtherVuz = False
    if PointOrderEnrollOtherVuz.objects.filter(student=student, order__isClosed=True).exists():
        isOtherVuz = True
    all_history_student = get_all_points_student_history(student=student).values('order', 'date')
    stipends = StudentStipend.objects.filter(student=student) \
        .annotate(order=F('group_stipend__pointorderstipend__order'), date=F('group_stipend__date_start')) \
        .values('order', 'date')
    all_history_student = list(all_history_student) + list(stipends)
    all_history_student = [{'order': Order.objects.get(id=x['order']), 'date': x['date']} for x in all_history_student
                           if x['order'] is not None]

    # костыль для добавления причины отчисления
    for order_info in all_history_student:
        order_info['type_order'] = order_info['order'].type_order.type_order
        dismiss_point = PointOrderDeductStudent.objects.filter(student=student, order=order_info['order']).first()
        if dismiss_point:
            order_info['type_order'] += f' ({dismiss_point.dict_reason})'

    all_history_student = sorted(all_history_student, key=lambda x: x['date'])

    all_history_orders_student = StudentHistoryOrder.objects.filter(student=student).order_by('date')
    health_info, list_check = get_health_info_student(student)
    student_documents = DocStudPersDep.objects.filter(student=student)

    sng = ['АЗЕРБАЙДЖАН', 'АРМЕНИЯ', 'БЕЛАРУСЬ', 'КАЗАХСТАН', 'Кыргызская Республика', 'МОЛДОВА, РЕСПУБЛИКА', 'РОССИЯ',
           'ТАДЖИКИСТАН', 'ТУРКМЕНИЯ', 'УЗБЕКИСТАН', 'УКРАИНА']
    is_foreign = student.info.citizen.citizen not in sng

    markbook_items, markbook_debts = [], []
    if hasattr(student, 'markbook'):
        markbook_items = student.markbook.markbookitem_set.all() \
            .order_by('session_subject__plan_semestr__number',
                      'session_subject__plan_semestr__subject__subject__name')

    markbook_debts = get_student_subjects_debts(student)

    return render(request, "student_info/student.html",
                  dict(student=student, relatives=relatives, isOtherVuz=isOtherVuz,
                       all_history_student=all_history_student,
                       all_history_orders_student=all_history_orders_student,
                       health_info=health_info, list_health_check=list_check,
                       student_documents=student_documents, is_foreign=is_foreign, markbook_items=markbook_items,
                       markbook_debts=markbook_debts))




def redact_person_doc(request, id_student):
    student = Student.objects.get(id=id_student)
    doc_type_all = DictDocType.objects.all()
    if request.method == "GET":
        return render(request, "redactFormStudent/redactPersDoc.html", dict(student=student, doc_type_all=doc_type_all))
    if request.method == "POST":
        person_doc = student.person_doc
        print(request.POST)

        if person_doc:
            pass
        else:
            person_doc = StudentPersonDoc()
            person_doc.save()
            student.person_doc = person_doc
            student.save()

        person_doc.doc_type = DictDocType.objects.get(doc=request.POST["doc_type"])
        doc_series = request.POST["doc_series"]
        doc_number = request.POST["doc_number"]
        person_doc.doc_series = doc_series
        person_doc.doc_number = doc_number

        if request.POST["doc_date"] != "" and request.POST["doc_date"] != "None":
            person_doc.doc_date = datetime.strptime(request.POST["doc_date"], "%d.%m.%Y")
        else:
            person_doc.doc_date = None
        person_doc.doc_dep_code = request.POST["doc_dep_code"]
        person_doc.doc_dep = request.POST["doc_dep"]
        person_doc.save()
        return redirect("/dekanat/student/" + str(student.id))




def redact_prev_edu(request, id_student):
    student = Student.objects.get(id=id_student)
    isOtherVuz = False
    if PointOrderEnrollOtherVuz.objects.filter(student=student, order__isClosed=True).exists():
        isOtherVuz = True
    prev_edu_level_all = DictPrevEduLevel.objects.all()
    prev_edu_doctype_all = DictPrevEduDocType.objects.all()
    prev_edu_doctype_all = prev_edu_doctype_all.model.PrevEduDocTypes
    prev_edu_doctype_all = sorted(prev_edu_doctype_all, key=lambda i: i[1])
    if request.method == "GET":
        return render(request, "redactFormStudent/redact_prev_edu.html", dict(student=student, isOtherVuz=isOtherVuz,
                                                                              prev_edu_level_all=prev_edu_level_all,
                                                                              prev_edu_doctype_all=prev_edu_doctype_all,
                                                                              ))
    if request.method == "POST":
        prev_edu = student.prev_edu

        if prev_edu:
            pass
        else:
            prev_edu = StudentPrevEdu()
            prev_edu.save()
            student.prev_edu = prev_edu
            student.save()
        if request.POST.get("edu_level"):
            prev_edu.prevEduLevel = DictPrevEduLevel.objects.get(prevEduLevel=request.POST.get("edu_level"))
        else:
            prev_edu.prevEduLevel = None
        prev_edu.prevEduOrg = request.POST.get("edu_org")
        if request.POST.get("year_end"):
            prev_edu.yearEnd = request.POST.get("year_end")
        else:
            prev_edu.yearEnd = None
        if request.POST.get("doc_type"):
            prev_edu.prevEduDocType = DictPrevEduDocType.objects.get(prevEduDocType=request.POST["doc_type"])
        else:
            prev_edu.prevEduDocType = None
        prev_edu.prevEduDocSer = request.POST.get("doc_ser")
        prev_edu.prevEduDocNum = request.POST.get("doc_num")
        prev_edu.is_prev_edu_orginal = request.POST.get("is_original")
        if request.POST.get("doc_date") != "" and request.POST.get("doc_date") != "None":
            prev_edu.prevEduDocDateGet = datetime.strptime(request.POST.get("doc_date"), "%d.%m.%Y")

        prev_edu.save()

        if isOtherVuz:
            other_vus_form = AnotherVuzDocForm(request.POST, instance=student.abit_info)
            other_vus_form.save()
            edit_another_vuz_doc(request, student)
        return redirect("/dekanat/student/" + str(student.id))


def set_address(address, post, name):
    if not post.get(name):
        return address
    if not address:
        address = Address.objects.create()
    obj = json.loads(post.get(name))
    update_address(address, obj)
    return address


def redact_private(request, id_student):
    student = Student.objects.get(id=id_student)
    ds = DictCitizen.objects.all()
    dl = DictLang.objects.all()
    relatives_type_all = DictRelativeDegree.objects.all()
    relatives = StudentRelative.objects.filter(student=student)

    if request.method == "GET":
        return render(request, "redactFormStudent/redactprivate.html", dict(student=student, ds=ds, dl=dl,
                                                                            relatives_type_all=relatives_type_all,
                                                                            relatives=relatives
                                                                            ))
    if request.method == "POST":
        info = student.info
        if not info:
            info = StudentInfo()
            info.save()
            student.info = info
            student.save()

        if request.POST["birthday"]:
            info.birthday = datetime.strptime(request.POST["birthday"], "%d.%m.%Y")

        info.gender = int(request.POST["gender"])
        info.citizen = DictCitizen.objects.get(id=request.POST["citizen"])
        info.foreign_lang = DictLang.objects.get(lang=request.POST["foreign_lang"])
        info.phone = request.POST["phone"]
        info.email = request.POST["email"]
        info.fact_address = set_address(info.fact_address, request.POST, "fact_address")
        if request.POST.get('reg_address') == 'copy':
            info.reg_address = copy(info.fact_address)
            info.reg_address.pk = None
            info.reg_address.save()
        else:
            info.reg_address = set_address(info.reg_address, request.POST, "reg_address")
        info.family_status = int(request.POST["family_status"])
        info.is_large_family = 'is_large_family' in request.POST
        info.is_orphan = "is_orphan" in request.POST
        info.is_chernobyl = "is_chernobyl" in request.POST
        info.children_count = request.POST.get('children_count')
        info.single_mother = 'is_single_mother' in request.POST
        info.payment_contract_number = request.POST.get('payment_contract')
        if "is_invalid" in request.POST:
            info.is_invalid = True
            if request.POST["invalid_group"]:
                info.invalid_group = request.POST["invalid_group"]
        else:
            info.is_invalid = False
            info.invalid_group = None

        info.save()

        in_hostel = "in_hostel" in request.POST
        if student.hostel:
            student.hostel.in_hostel = in_hostel
            student.hostel.save()
        elif in_hostel:
            StudentHostel.objects.create(in_hostel=in_hostel, student=student)

        return redirect("/dekanat/student/" + str(student.id))


def get_relative_student(request):
    if request.method == "POST":
        relativ_id = request.POST.get('id_relative')
        relativ = StudentRelative.objects.get(id=relativ_id)
        relativ_dict = model_to_dict(relativ)
        birthday_str = relativ_dict['birthday']
        if birthday_str:
            relativ_dict['birthday'] = datetime.strftime(birthday_str, "%d.%m.%Y")
        return JsonResponse(relativ_dict)

    return None


def get_history_order_student(request):
    if request.method == "POST":
        order_id = request.POST.get('id_order')
        order = StudentHistoryOrder.objects.get(id=order_id)
        relativ_dict = model_to_dict(order)
        date_str = relativ_dict['date']
        if date_str:
            relativ_dict['date'] = datetime.strftime(date_str, "%d.%m.%Y")
        return JsonResponse(relativ_dict)
    return None


def delete_history_order_student(request):
    if request.method == "POST":
        order_id = request.POST.get('id_order')
        order = StudentHistoryOrder.objects.get(id=order_id)
        order.delete()
        return JsonResponse(order_id, safe=False)
    return None


def redact_history_order(request, id_student):
    student = Student.objects.get(id=id_student)
    all_history_orders_student = StudentHistoryOrder.objects.filter(student=student).order_by('date')
    type_order = DictTypeOrder.objects.all()
    depart_all = EduDepartment.objects.filter(type=1)  # 1 - институты
    if request.method == "GET":
        return render(request, "redactFormStudent/redact_history_order.html", dict(student=student,
                                                                                   type_order=type_order,
                                                                                   depart_all=depart_all,
                                                                                   all_history_orders_student=all_history_orders_student))
    if request.method == 'POST':
        id_order = request.POST.get("id_history_order")
        if id_order:
            history_order = StudentHistoryOrder.objects.get(id=id_order)
        else:
            history_order = StudentHistoryOrder()
        history_order.student = student
        history_order.number = request.POST.get('number_order')
        if request.POST["date_order"] != "" and request.POST["date_order"] != "None":
            history_order.date = datetime.strptime(request.POST["date_order"], "%d.%m.%Y")
        else:
            history_order.date = None
        if request.POST["depart_select"]:
            history_order.department = EduDepartment.objects.get(id=request.POST["depart_select"])
        else:
            history_order.department = None
        if request.POST["order_type_select"]:
            history_order.type_order = DictTypeOrder.objects.get(id=request.POST["order_type_select"])
        else:
            history_order.type_order = None
        history_order.save()
    return redirect("/dekanat/student/" + str(id_student))


def edit_relative_student(request, id_student):
    student = Student.objects.get(id=id_student)
    id_relative = request.POST['relative_id']
    try:
        relative = StudentRelative.objects.get(pk=id_relative)
    except:
        relative = StudentRelative()
        relative.student = student
    if request.POST['relative_type_select']:
        relative.type = DictRelativeDegree.objects.get(relativeDegree_type=request.POST['relative_type_select'])

    relative.surname = request.POST['surname_relative']
    relative.name = request.POST['name_relative']
    relative.patronymic = request.POST['patronymic_relative']

    if request.POST['birthday_relative']:
        relative.birthday = datetime.strptime(request.POST['birthday_relative'], "%d.%m.%Y")

    relative.address = request.POST['address_relative']
    # if request.POST['address_kladr']:
    #   relative.address_kladr = int(request.POST["address_kladr"])

    relative.work_place = request.POST["work_place"]
    relative.post = request.POST["post"]
    relative.phone = request.POST["phone_relative"]
    relative.email = request.POST["email_relative"]
    relative.sms = "is_sms" in request.POST

    relative.save()
    return HttpResponse("Ok")


def redact_military_info(request, id_student):
    student = Student.objects.get(id=id_student)
    if request.method == 'POST':
        mil_info = student.mil_info
        if not mil_info:
            mil_info = StudentMilitaryControl.objects.create()
            student.mil_info = mil_info
            student.save()

        mil_info.is_mil_reg = 'is_mil_reg' in request.POST
        if request.POST.get('mil_cat'):
            mil_info.category = int(request.POST.get('mil_cat'))
        else:
            mil_info.category = None
        if request.POST.get('mil_office'):
            mil_info.mil_office = DictMilOffice.objects.get(id=int(request.POST.get('mil_office')))
        else:
            mil_info.mil_office = None

        mil_info.comment = request.POST.get('comment')
        mil_info.is_mil_kaf = 'is_mil_kaf' in request.POST
        mil_info.contract_number = request.POST.get('contract_number')
        contract_date = request.POST.get("contract_date")
        if contract_date:
            mil_info.contract_date = datetime.strptime(contract_date, "%d.%m.%Y")
        else:
            mil_info.contract_date = None

        start_contract_date = request.POST.get("start_contract_date")
        if start_contract_date:
            mil_info.start_contract_date = datetime.strptime(start_contract_date, "%d.%m.%Y")
        else:
            mil_info.start_contract_date = None

        end_contract_date = request.POST.get("end_contract_date")
        if end_contract_date:
            mil_info.end_contract_date = datetime.strptime(end_contract_date, "%d.%m.%Y")
        else:
            mil_info.end_contract_date = None

        if request.POST.get('mil_edu_program'):
            mil_info.mil_kaf_edu_program = int(request.POST.get('mil_edu_program'))
        else:
            mil_info.mil_kaf_edu_program = None
        mil_info.save()

    offices = DictMilOffice.objects.all().order_by('locality')
    countries = DictCitizen.objects.all()

    return render(request, 'redactFormStudent/redact_military_info.html',
                  dict(student=student, categories=StudentMilitaryControl.mil_categories, offices=offices,
                       mil_edu_programmes=StudentMilitaryControl.mil_kaf_edu_programes, countries=countries))


def edit_another_vuz_doc(request, student):
    student_abit_info = student.abit_info
    if request.method == "POST":
        student_abit_info.another_doc_type = int(request.POST.get('old_doc_type'))
        student_abit_info.another_doc_series = request.POST.get('another_doc_seria')
        student_abit_info.another_doc_number = request.POST.get('another_doc_num')
        student_abit_info.another_name = request.POST.get('another_vuz_name')
        student_abit_info.another_year_start = int(request.POST.get('another_year_start'))
        student_abit_info.save()
    return "Ok"


def redact_infoenroll(request, id_student):
    student = Student.objects.get(id=id_student)
    student_abit_info = student.abit_info
    if request.method == "GET":
        return render(request, "redactFormStudent/redact_infoenroll.html", dict(student_info=student_abit_info,
                                                                                student_fio=student.short_name(),
                                                                                student_id=id_student))
    if request.method == 'POST':
        student_abit_info.ent_doc_num = request.POST.get('ent_doc_num')
        if request.POST["ent_doc_date"] != "" and request.POST["ent_doc_date"] != "None":
            student_abit_info.ent_doc_date = datetime.strptime(request.POST["ent_doc_date"], "%d.%m.%Y")
        else:
            student_abit_info.ent_doc_date = None
        student_abit_info.abit_is_direction = 'is_direction' in request.POST
        student_abit_info.save()
    return redirect("/dekanat/student/" + str(id_student))


def upload_photo_student(request):
    id_student = request.POST.get("id_student")
    student = Student.objects.get(id=id_student)
    if request.method == 'POST':
        info = student.info
        if not info:
            info = StudentInfo()
            info.save()
            student.info = info
            student.save()
        if request.FILES['photo']:
            info.photo = request.FILES['photo']
            info.save()
    return redirect("/dekanat/student/" + str(student.id))


def delete_photo_student(request, id_student):
    student = Student.objects.get(id=id_student)
    info = student.info
    if info:
        info.photo = None
        info.save()
    return redirect("/dekanat/student/" + str(student.id))


def calculation_index(health_check):
    rez_dict = dict()
    summ_point = 0
    try:
        ketle_index = health_check.weight / (health_check.height * health_check.height / 10000)
        if ketle_index > 28.1:
            ketle_index_point = 2
        elif ketle_index >= 25.1:
            ketle_index_point = 1
        elif ketle_index >= 20.1:
            ketle_index_point = 0
        elif ketle_index >= 19:
            ketle_index_point = -1
        else:
            ketle_index_point = -2
        rez_dict['ketle_index'] = round(ketle_index, 2)
        rez_dict['ketle_index_point'] = ketle_index_point
        summ_point += ketle_index_point
    except:
        rez_dict['ketle_index'] = None
        rez_dict['ketle_index_point'] = None

    try:
        life_index = health_check.lung_capacity / health_check.weight
        if life_index > 66:
            life_index_point = 3
        elif life_index >= 61:
            life_index_point = 2
        elif life_index >= 56:
            life_index_point = 1
        elif life_index >= 51:
            life_index_point = 0
        else:
            life_index_point = -1
        rez_dict['life_index'] = round(life_index, 2)
        rez_dict['life_index_point'] = life_index_point
        summ_point += life_index_point
    except:
        rez_dict['life_index'] = None
        rez_dict['life_index_point'] = None

    try:
        power_index = ((health_check.dyn_left + health_check.dyn_right) / 2) * 100 / health_check.weight
        if power_index > 80:
            power_index_point = 3
        elif power_index >= 71:
            power_index_point = 2
        elif power_index >= 66:
            power_index_point = 1
        elif power_index >= 61:
            power_index_point = 0
        else:
            power_index_point = -1
        rez_dict['power_index'] = round(power_index, 2)
        rez_dict['power_index_point'] = power_index_point
        summ_point += power_index_point
    except:
        rez_dict['power_index'] = None
        rez_dict['power_index_point'] = None

    try:
        robinson_index = health_check.resting_heart_rate * health_check.sys_blood_pres / 100
        if robinson_index >= 111:
            robinson_index_point = -2
        elif robinson_index >= 95:
            robinson_index_point = -1
        elif robinson_index >= 85:
            robinson_index_point = 0
        elif robinson_index >= 70:
            robinson_index_point = 3
        else:
            robinson_index_point = 5
        rez_dict['robinson_index'] = round(robinson_index, 2)
        rez_dict['robinson_index_point'] = robinson_index_point
        summ_point += robinson_index_point
    except:
        rez_dict['robinson_index'] = None
        rez_dict['robinson_index_point'] = None

    try:
        recovery_time = health_check.recovery_time
        if recovery_time > 150:
            recovery_time_point = -2
        elif recovery_time >= 120:
            recovery_time_point = 1
        elif recovery_time >= 90:
            recovery_time_point = 3
        elif recovery_time >= 60:
            recovery_time_point = 5
        else:
            recovery_time_point = 7
        rez_dict['recovery_time'] = round(recovery_time, 2)
        rez_dict['recovery_time_point'] = recovery_time_point
        summ_point += recovery_time_point
    except:
        rez_dict['recovery_time'] = None
        rez_dict['recovery_time_point'] = None

    rez_dict['summ_point'] = summ_point
    return rez_dict


def render_health_info(request, id_student):
    student = Student.objects.get(id=id_student)
    if request.method == 'GET':
        health_info, list_check = get_health_info_student(student)
        phys_cult_groups = HealthCheck.phys_cult_groups
        health_groups = HealthCheck.health_groups

        return render(request, 'redactFormStudent/redact_health_info.html',
                      dict(student=student, health_info=health_info, list_health_check=list_check,
                           phys_cult_groups=phys_cult_groups, health_groups=health_groups))


def get_or_create_student_health(student):
    health_info = student.health_check
    if not health_info:
        health_info = StudentHealth.objects.create()
        student.health_check = health_info
        student.save()
    return health_info


def change_fluoro_last_date(request, id_student):
    student = Student.objects.get(id=id_student)
    health_info = get_or_create_student_health(student)
    health_info.fluoro_last_date = get_date_from_requests(request, "date_fluorography")
    health_info.save()
    return HttpResponse("/dekanat/student/" + str(student.id))


def get_last_check(request, id_student):
    student = Student.objects.get(id=id_student)
    health_info = student.health_check
    last_check = HealthCheck.objects.filter(health_check=health_info).order_by('-check_date').first()
    if last_check:
        # last_check.check_date = datetime.strftime(last_check.check_date, "%d.%m.%Y")
        return JsonResponse(model_to_dict(last_check))
    else:
        return HttpResponse(None)


def get_index_health(request, id_student):
    student = Student.objects.get(id=id_student)
    if request.method == 'GET':
        health_check = HealthCheck.objects.get(id=request.GET.get("health_id"))
        all_index = calculation_index(health_check)
        result_table = f"<tr><td>Индекс Кетле</td><td>{all_index['ketle_index']}</td>" \
                       f"<td>{all_index['ketle_index_point']}</td></tr>" \
                       f"<tr><td>Жизненный индекс</td><td>{all_index['life_index']}</td>" \
                       f"<td>{all_index['life_index_point']}</td></tr>" \
                       f"<tr><td>Силовой индекс</td><td>{all_index['power_index']}</td>" \
                       f"<td>{all_index['power_index_point']}</td></tr>" \
                       f"<tr><td>Индекс Робинсона</td><td>{all_index['robinson_index']}</td>" \
                       f"<td>{all_index['robinson_index_point']}</td></tr>" \
                       f"<tr><td>Время восстановления</td><td>{all_index['recovery_time']}</td>" \
                       f"<td>{all_index['recovery_time_point']}</td></tr>"
        return JsonResponse({'table_body': result_table.replace('None', '')})
    else:
        return None


def edit_healt_check(request, id_student):
    student = Student.objects.get(id=id_student)
    if request.method == 'POST':
        if request.POST.get("health_id"):
            health_check = HealthCheck.objects.get(id=request.POST.get("health_id"))
        else:
            health_info = get_or_create_student_health(student)
            health_check = HealthCheck.objects.create(health_check=health_info)
        # health_check.check_date = get_date_from_requests(request, "check_date_modal")
        health_check.phys_cult_group = get_char_from_request(request, "phys_group_select")
        health_check.health_group = get_char_from_request(request, "phys_group_select")
        health_check.diagnosis = get_char_from_request(request, "diagnosis_modal")
        health_check.save()
        return HttpResponse(health_check.id)


def edit_params_healt(request, id_student):
    student = Student.objects.get(id=id_student)
    is_new_health = False
    if request.method == 'POST':
        if request.POST.get("health_param_id"):
            health_check = HealthCheck.objects.get(id=request.POST.get("health_param_id"))
        else:
            health_info = get_or_create_student_health(student)
            health_check = HealthCheck.objects.create(health_check=health_info)
            is_new_health = True
        try:
            health_check.check_date = get_date_from_requests(request, "check_date_modal")
            health_check.resting_heart_rate = get_int_from_request(request, "resting_heart_rate_modal")
            health_check.weight = get_float_from_request(request, "weight_modal")
            health_check.height = get_float_from_request(request, "height_modal")
            health_check.lung_capacity = get_int_from_request(request, "lung_capacity_modal")
            health_check.dyn_left = get_int_from_request(request, "dyn_left_modal")
            health_check.dyn_right = get_int_from_request(request, "dyn_right_modal")
            health_check.sys_blood_pres = get_int_from_request(request, "sys_blood_pres_modal")
            health_check.dias_blood_pres = get_int_from_request(request, "dias_blood_pres_modal")
            health_check.recovery_time = get_int_from_request(request, "recovery_time_modal")
            health_check.summ_point_index = calculation_index(health_check)['summ_point']
            health_check.save()
        except:
            if is_new_health:
                health_check.delete()
            return HttpResponseBadRequest("Ошибка! Данные заполнены неправильно.")
        return HttpResponse(health_check.id)


def get_healt_check(request):
    try:
        health_check = HealthCheck.objects.get(id=request.POST.get("id_health"))
        health_check.check_date = datetime.strftime(health_check.check_date, "%d.%m.%Y")
        return JsonResponse(model_to_dict(health_check))
    except:
        return HttpResponse(None)


def delete_healt_check(request):
    health_check = HealthCheck.objects.get(id=request.POST.get("id_health"))
    health_check.delete()
    return HttpResponse("Ок")


def edit_student_hostel(request, id_student):
    student = Student.objects.get(id=id_student)
    if request.method == 'GET':
        form = HostelForm(instance=student.hostel)
        return render(request, 'redactFormStudent/redact_student_hostel_info.html', dict(student=student, form=form))
    elif request.method == 'POST':
        hostel = student.hostel
        if not hostel:
            hostel = StudentHostel.objects.create(student=student)
            student.hostel = hostel
            student.save()

        form = HostelForm(request.POST, instance=hostel)
        form.save()
        return redirect("/dekanat/student/" + str(student.id) + "/#yak_student_hostel")


def render_table_student_doc(request, student_id):
    student = Student.objects.get(id=student_id)
    items = DocStudPersDep.objects.filter(student=student)
    table_stud_docs = render_to_string('redactFormStudent/student_documents_table.html',
                                       dict(student=student, items=items))
    other_docs = OtherDocStudPersDep.objects.get_or_create(student=student)
    return JsonResponse({"table_stud_docs": table_stud_docs, "other_docs": str(other_docs[0])})


def get_student_doc_table(request, student_id):
    student = Student.objects.get(id=student_id)
    items = DocStudPersDep.objects.filter(student=student)
    return render(request, 'redactFormStudent/student_documents_table.html', dict(student=student, items=items))


def get_dicts_for_modal_student_doc():
    depart_all = EduDepartment.objects.all().order_by('name')
    dep_id165 = Department.objects.get(id=165)  # отдел по работе со студенческим контингентом
    status_all = DocStudPersDep.StatusChoices
    doctype_stud_pers_dep_all = DictStudPersDepDocType.objects.all()
    return dict(depart_all=depart_all, dep_id165=dep_id165, status_all=status_all,
                doctype_stud_pers_dep_all=doctype_stud_pers_dep_all)


def redact_student_documents(request):
    id_student = request.GET.get("id")
    student = Student.objects.get(id=id_student)
    all_documents_student = DocStudPersDep.objects.filter(student=student)
    dicts = get_dicts_for_modal_student_doc()
    if request.method == "GET":
        dep = request.curr_dep
        tree = get_tree('contingent_students', dep)
        return render(request, "redactFormStudent/redact_student_documents.html", dict(student=student,
                                                                                       all_documents_student=all_documents_student,
                                                                                       tree=tree,
                                                                                       dicts=dicts,
                                                                                       ))
    if request.method == 'POST':
        id_doc = request.POST.get("id_record")
        if id_doc:
            document = DocStudPersDep.objects.get(id=id_doc)
        else:
            document = DocStudPersDep()
        document.student = student
        document.series = request.POST.get('series_doc')
        document.number = request.POST.get('number_doc')

        if request.POST.get("doc_type"):
            document.type_doc = DictStudPersDepDocType.objects.get(pk=request.POST["doc_type"])
        else:
            document.type_doc = None

        if request.POST.get("depart_select", False):
            document.location = Department.objects.get(id=request.POST["depart_select"])
        else:
            document.location = None
        document.sign = request.POST.get("sign_select")
        document.status = get_char_from_request(request, "status_select")
        document.save()
    return redirect("/dekanat/student/student_doc_dep/student_documents/" + str(id_student))


def get_document_student(request):
    if request.method == "POST":
        doc_id = request.POST.get('id_record')
        document = DocStudPersDep.objects.get(id=doc_id)
        relativ_dict = model_to_dict(document)
        relativ_dict['doc_date'] = datetime.strftime(document.doc_date, "%d.%m.%Y")
        return JsonResponse(relativ_dict)
    return None


def delete_student_document(request):
    if request.method == "POST":
        doc_id = request.POST.get('id_record')
        doc = DocStudPersDep.objects.get(id=doc_id)
        doc.delete()
        return JsonResponse(doc_id, safe=False)
    return None


def find_value_dict_doc_stud_pers(search_value):
    """
    Найти в словаре типов документов для студ отдела кадров (DictStudPersDepDocType) запись,
    включающую строку search_value
    :param search_value:
    :return:
    """

    for value_dict in DictStudPersDepDocType.StudPersDepDocType:
        rez = str(value_dict[1]).find(search_value)
        if rez != -1:
            type = DictStudPersDepDocType.objects.get(studPersDepDocType=value_dict[0])
            return type
    return None


def generate_student_doc_dep(student):
    # создать личное дело
    location = Department.objects.get(id=165)  # отдел по работе со студенческим контингентом
    document = DocStudPersDep(student=student,
                              type_doc=DictStudPersDepDocType.objects.get(studPersDepDocType=0),  # Личное дело
                              status=1,  # в подразделении
                              sign=True,  # оригинал
                              location=location,
                              )
    document.save()

    # создать документ об образовании и заполнить из student.prev_edu
    prev_edu = student.prev_edu
    document = DocStudPersDep(student=student,
                              series=prev_edu.prevEduDocSer,
                              number=prev_edu.prevEduDocNum,
                              status=2,  # в личном деле
                              sign=prev_edu.is_prev_edu_orginal,
                              )
    str_prev_edu = str(prev_edu.prevEduDocType)
    type = find_value_dict_doc_stud_pers(str_prev_edu)
    if type is not None:
        document.type_doc = type
    document.save()

    # если из другого вуза создать документ
    abit_info = student.abit_info
    if abit_info.another_type == True:
        document = DocStudPersDep(student=student,
                                  series=abit_info.another_doc_series,
                                  number=abit_info.another_doc_number,
                                  status=2,  # в личном деле
                                  sign=0,  # оригинал
                                  )
        if abit_info.another_doc_type is not None:
            str_type_doc = (abit_info.another_doc_type_choice[abit_info.another_doc_type][1]).capitalize()
            type = find_value_dict_doc_stud_pers(str_type_doc)
            if type is not None:
                document.type_doc = type
        document.save()
    return None


def init_doc_student(request):
    """
    Удалить все документы студента и
    сформировать личное дело, документ об образовании и документ их предыдущего ВУЗа (generate_student_doc_dep())
    :param request:
    :return:
    """
    id_student = request.GET.get("id")
    student = Student.objects.get(id=id_student)
    DocStudPersDep.objects.filter(student=student).delete()
    generate_student_doc_dep(student)
    return JsonResponse(student.id, safe=False)
