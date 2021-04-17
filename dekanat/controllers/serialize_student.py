from dekanat.controllers.student_reference import get_student_reference_orders
from orders.models import PointOrderDeductStudent


# функции для сериализации полей в студенте, группа передается в каждую функцию для универсализации вызова
# функции должны назваться get_<имя поля в fields в serialize_student>

def get_name(student):
    return str(student.name)


def get_surname(student):
    return str(student.surname)


def get_patronymic(student):
    return str(student.patronymic)


def get_full_name(student):
    return str(student)


def get_short_name(student):
    return student.short_name()


def get_birthday(student):
    return str(student.info.birthday.strftime('%d.%m.%Y'))


def get_gender(student):
    return student.info.get_gender_display()


def get_citizen(student):
    return str(student.info.citizen)


def get_foreign_lang(student):
    return str(student.info.foreign_lang)


def get_phone(student):
    return student.info.phone or student.info.phone_1c or ''


def get_email(student):
    return student.info.email


def get_reg_address(student):
    return str(student.info.reg_address)


def get_fact_address(student):
    return str(student.info.fact_address)


def get_is_invalid(student):
    return 'да' if student.info.is_invalid else 'нет'


def get_is_large_family(student):
    return 'да' if student.info.is_large_family else 'нет'


def get_is_orphan(student):
    return 'да' if student.info.is_orphan else 'нет'


def get_is_chernobyl(student):
    return 'да' if student.info.is_chernobyl else 'нет'


def get_is_starosta(student):
    return 'да' if student.starosta.exists() else 'нет'


def get_is_direction(student):
    return 'да' if student.abit_info.abit_is_direction else 'нет'


def get_zcode(student):
    return student.zcode


def get_tutor(student):
    return str(student.diploma_tutor)


def get_diploma_theme(student):
    return str(student.diploma_theme)


def get_group(student):
    return student.group.name_group


def get_group_created_year(student):
    return student.group.created_year


def get_kaf(student):
    return student.plan.spec.producing_dep


def get_institute(student):
    return str(student.group.dep.get_institute().smallname)


def get_kurs(student):
    return str(student.kurs)


def get_edu_form(student):
    return student.group.spec_group.eduForm.get_smallname()


def get_edu_type(student):
    return str(student.edu_type.get_smallname())


def get_level(student):
    return str(student.plan.spec.spec.level)


def get_spec(student):
    return str(student.group.spec_group.spec)


def get_subspec(student):
    return str(student.plan.spec.spec)


def get_spec_code(student):
    return str(student.group.spec_group.code())


def get_subspec_code(student):
    return str(student.plan.spec.code())


def get_spec_name(student):
    return str(student.group.spec_group.spec.name)


def get_subspec_name(student):
    return str(student.plan.spec.spec.name)


def get_ent_doc_num(student):
    return student.abit_info.ent_doc_num


def get_ent_doc_date(student):
    if student.abit_info.ent_doc_date:
        return student.abit_info.ent_doc_date.strftime('%d.%m.%Y')
    else:
        return ''


def get_deduct_order_num(student):
    point_order = PointOrderDeductStudent.objects.filter(student=student, order__isClosed=True).first()
    if point_order:
        return point_order.order.name


def get_deduct_order_date(student):
    point_order = PointOrderDeductStudent.objects.filter(student=student, order__isClosed=True).first()
    if point_order:
        return point_order.order.date.strftime('%d.%m.%Y')


def get_is_mil_reg(student):
    return 'да' if student.mil_info.is_mil_reg else 'нет'


def get_category(student):
    return student.mil_info.get_category_display()


def get_mil_office(student):
    return str(student.mil_info.mil_office.name) if student.mil_info.mil_office else ''


def get_is_mil_kaf(student):
    return 'да' if student.mil_info.is_mil_kaf else 'нет'


def get_mil_kaf_edu_program(student):
    return student.mil_info.get_mil_kaf_edu_program_display()


def get_empty(student):
    return ''


def get_prev_edu_level(student):
    return str(student.prev_edu.prevEduLevel)


def get_prev_edu_org(student):
    return str(student.prev_edu.prevEduOrg)


def get_prev_edu_end_year(student):
    return str(student.prev_edu.prevEduDocDateGet.year) if student.prev_edu.prevEduDocDateGet else ''


def get_last_fluoru_date(student):
    if student.health_check and student.health_check.fluoro_last_date:
        return student.health_check.fluoro_last_date.strftime('%d.%m.%Y')
    return ''


def get_payment_contract_number(student):
    return student.info.payment_contract_number if student.info.payment_contract_number else ''


def get_debt(student):
    if student.debt:
        return str(student.debt.semestr1 + student.debt.semestr2 + student.debt.last_debt)
    return ''


def get_orders(student):
    orders = get_student_reference_orders(student)
    orders = [f'{o["order_title"]} (приказ № {o["order_name"]} от {o["order_date"].strftime("%d.%m.%Y")})' for o in
              orders]
    if orders:
        return ' ;'.join(orders)
    return ''


def get_snils(student):
    if student.docs:
        return student.docs.snils_number
    return ''


def get_is_snils(student):
    return 'да' if student.docs and student.docs.snils_number else 'нет'


def get_children_count(student):
    return student.info.children_count


def serialize_student(student, fields):
    """
    :param student: Student или StudentHistory
    :param fields: список наименований полей, которые нужно сериализовать
    :param date: дата в истории по которой нужно взять поля
    :return: список диктов с данными о студенте
    """
    d = dict()
    d['id'] = student.id
    for field in fields:
        f = globals()["get_" + field](student)
        d[field] = f if f != 'None' else ''
    return d
