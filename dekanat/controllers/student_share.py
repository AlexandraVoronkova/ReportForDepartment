import logging
import re
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from dekanat.controllers.utils import update_address
from dekanat.models.student import Student, StudentInfo, StudentAbitInfo, StudentPersonDoc, StudentHostel, \
    StudentPrevEdu, StudentMilitaryControl, StudentBankDetails
from dekanat.views.cardStudent import generate_student_doc_dep
from dict_app.models_.address import Address
from dict_app.models_.depart import EduDepartment
from dict_app.models_.dict import DictLang, DictPrevEduDocType, DictPrevEduLevel, DictCitizen, DictDocType, DictEduType
from history_app.controllers.student_controller import init


def correct_date(dt_text):
    return datetime.strptime(dt_text, '%d.%m.%Y')


def get_dict_obj(model, choices, field_name, search):
    for choice in choices:
        if choice[1] == search:
            return model.objects.get(**{field_name: choice[0]})


def get_one_phone(phone_str):
    phone_str = re.split(';|,', phone_str)[0]
    one_phone = re.sub("\D", "", phone_str)
    if len(one_phone) == 11:
        if one_phone[0] == '7' or one_phone[0] == '8':
            one_phone = '+7' + one_phone[1:]
        return one_phone
    return None


def create_abiturient(kod_1c, surname, name, patronymic, gender, birthday_text, doc_type_text, doc_series,
                      doc_number, doc_date_text, doc_dep, citizen_text, reg_address_obj, fact_address_obj, email,
                      uid, prevEduLevel_text, prevEduOrg, prevEduDocDateGet_text, prevEduDocType_text,
                      prevEduDocSer, prevEduDocNum, original_doc, abit_spec_code, abit_spec_name, abit_subspec_code,
                      abit_subspec_name, abit_edu_form, edu_type, ent_doc_num, ent_doc_date_text,
                      foreign_lang_text, phone, institute_id):
    logger = logging.getLogger('abiturient_import')

    birthday = correct_date(birthday_text)
    doc_date = correct_date(doc_date_text)
    ent_doc_date = correct_date(ent_doc_date_text)
    prevEduDocDateGet = correct_date(prevEduDocDateGet_text)

    try:
        Student.objects.get(uid=uid, abit_info__ent_doc_num=ent_doc_num, abit_info__ent_doc_date=ent_doc_date)
    except ObjectDoesNotExist:
        foreign_lang = get_dict_obj(DictLang, DictLang.Langs, 'lang', foreign_lang_text)
        if not foreign_lang:
            logger.warning('У абитуриента {} неверный иностранный язык - {}'.format(uid, foreign_lang_text))

        prevEduDocType = get_dict_obj(DictPrevEduDocType, DictPrevEduDocType.PrevEduDocTypes,
                                      'prevEduDocType', prevEduDocType_text)
        if not prevEduDocType:
            logger.warning('У абитуриента {} неверный тип документа о предыдущем образовании - {}'.format(uid,
                                                                                                          prevEduDocType_text))

        prevEduLevel = get_dict_obj(DictPrevEduLevel, DictPrevEduLevel.PrevEduLevels,
                                    'prevEduLevel', prevEduLevel_text)
        if not prevEduLevel:
            logger.warning(
                'У абитуриента {} неверный уровень предыдущего образования - {}'.format(uid, prevEduLevel_text))

        citizen = None
        if citizen_text:
            try:
                citizen = DictCitizen.objects.get(citizen=citizen_text)
            except ObjectDoesNotExist:
                citizen = DictCitizen.objects.create(citizen=citizen_text)
            except MultipleObjectsReturned:
                logger.warning('В справочнике несколько одинаковых стран'.format(uid, citizen_text))

        doc_type = get_dict_obj(DictDocType, DictDocType.Docs, 'doc', doc_type_text)
        if not doc_type:
            logger.warning('У абитуриента {} неверный вид документа, удост. личность - {}'.format(uid, doc_type_text))

        fact_address = None
        reg_address = None
        if fact_address_obj:
            country = DictCitizen.objects.filter(citizen=fact_address_obj['country']).first()
            fact_address = Address.objects.create(country=country)
            update_address(fact_address, fact_address_obj)

        if reg_address_obj:
            country = DictCitizen.objects.filter(citizen=reg_address_obj['country']).first()
            reg_address = Address.objects.create(country=country)
            update_address(reg_address, reg_address_obj)

        phone_1c = phone
        one_phone = get_one_phone(phone_1c)

        studentInfo = StudentInfo(gender=gender, birthday=birthday, citizen=citizen, email=email,
                                  foreign_lang=foreign_lang, phone_1c=phone_1c, phone=one_phone,
                                  fact_address=fact_address, reg_address=reg_address)

        studentInfo.save()

        studentAbitInfo = StudentAbitInfo(abit_spec_code=abit_spec_code, abit_spec_name=abit_spec_name,
                                          abit_edu_form=abit_edu_form, abit_subspec_code=abit_subspec_code,
                                          abit_subspec_name=abit_subspec_name, ent_doc_num=ent_doc_num,
                                          ent_doc_date=ent_doc_date, id_1c=kod_1c)

        try:
            institute = EduDepartment.objects.get(_id=institute_id, freedate__isnull=True)
            studentAbitInfo.abit_dep = institute
        except ObjectDoesNotExist:
            logger.warning('Нет подразделения {}'.format(institute_id))
        except MultipleObjectsReturned:
            logger.warning('Несколько подразделений с одинаковым наименованием'.format(institute_id))
            studentAbitInfo.abit_dep = EduDepartment.objects.filter(name=institute_id,
                                                                    freedate__isnull=True).first()
        studentAbitInfo.save()

        student_person_docs = StudentPersonDoc(doc_type=doc_type, doc_number=doc_number, doc_series=doc_series,
                                               doc_date=doc_date, doc_dep=doc_dep)
        student_person_docs.save()

        studentPrevEdu = StudentPrevEdu(prevEduDocType=prevEduDocType, prevEduLevel=prevEduLevel,
                                        prevEduDocSer=prevEduDocSer,
                                        prevEduDocNum=prevEduDocNum, prevEduDocDateGet=prevEduDocDateGet,
                                        prevEduOrg=prevEduOrg, is_prev_edu_orginal=int(original_doc), )
        studentPrevEdu.save()

        mil_info = StudentMilitaryControl.objects.create()

        abiturient = Student.objects.create(uid=uid, status=0, name=name, surname=surname, patronymic=patronymic,
                                            info=studentInfo, prev_edu=studentPrevEdu,
                                            person_doc=student_person_docs, abit_info=studentAbitInfo,
                                            mil_info=mil_info)

        et = DictEduType.objects.get(edu_type=edu_type)
        abiturient.edu_type = et
        abiturient.status = 0
        abiturient.save()
        init(abiturient, ent_doc_date)
        # init(abiturient, datetime.now().date())
        generate_student_doc_dep(abiturient)  # документы для студ. отдела кадров
        return abiturient

    except MultipleObjectsReturned:
        logger.error('Несколько студентов с сочетанием uid, дата и номер приказа {} {} {}', uid, ent_doc_num,
                     ent_doc_date)


def create_empty_abiturient(surname, name, patronymic, gender, birthday, doc_series,
                            doc_number, with_other_vuz=False, status=0, zcode=None, uid=None,
                            date_create_abitur=datetime.now().date()):
    """
    Создание абитуриента для приказа "зачислить абитуриента из другого ВУЗа"
    :param surname:
    :param name:
    :param patronymic:
    :param gender:
    :param birthday_text:
    :param doc_series:
    :param doc_number:
    :return:
    """
    docs = StudentPersonDoc(doc_series=doc_series, doc_number=doc_number)
    docs.save()
    info = StudentInfo(birthday=birthday, gender=int(gender))
    info.save()
    bank_details = StudentBankDetails()
    bank_details.save()
    prev_edu = StudentPrevEdu()
    prev_edu.save()
    abit = StudentAbitInfo(another_type=with_other_vuz)
    abit.save()
    mil_info = StudentMilitaryControl()
    mil_info.save()
    abiturient = Student(status=status, name=name, surname=surname, patronymic=patronymic, person_doc=docs, info=info,
                         bank_details=bank_details, prev_edu=prev_edu, mil_info=mil_info,
                         abit_info=abit, zcode=zcode, uid=uid)
    abiturient.save()
    init(abiturient, date_create_abitur)
    generate_student_doc_dep(abiturient)  # документы для студ. отдела кадров
    return abiturient
