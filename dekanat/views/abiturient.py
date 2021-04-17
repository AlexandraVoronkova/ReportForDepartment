# -*- coding: utf-8 -*-
import codecs
import csv
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from dekanat.controllers import student_share
from dekanat.models import Student, EduDepartment


def create_address(field_name, row):
    if row[field_name + 'Адрес']:
        address = {}
        address['country'] = row[field_name + 'Страна']
        if row[field_name + 'Регион']:
            region = row[field_name + 'Регион'].split(' ')
            address['region'] = ' '.join(region[:-1])
            address['region_type'] = region[-1]

        if row[field_name + 'Район']:
            address['district'] = ' '.join(row[field_name + 'Район'].split(' ')[:1])

        if row[field_name + 'Город']:
            settlement = row[field_name + 'Город'].split(' ')
            address['settlement'] = ' '.join(settlement[:-1])
            address['settlement_type'] = settlement[-1]

        if row[field_name + 'НаселенныйПункт']:
            settlement = row[field_name + 'НаселенныйПункт'].split(' ')
            address['settlement'] = ' '.join(settlement[:-1])
            address['settlement_type'] = settlement[-1]

        if row[field_name + 'Улица']:
            street = row[field_name + 'Улица'].split(' ')
            address['street'] = ' '.join(street[:-1])
            address['street_type'] = street[-1]

        if row[field_name + 'Дом']:
            address['building'] = row[field_name + 'Дом']
        if row[field_name + 'Квартира']:
            address['flat'] = row[field_name + 'Квартира']

        address['index'] = row[field_name + 'Индекс']

        if row[field_name + 'КодАдресаКЛАДР']:
            kladr = row[field_name + 'КодАдресаКЛАДР'].split()
            address['kladr_id'] = ''.join(kladr)
        return address


levels_dict = {'Бакалавр': 'Бакалавр',
               'Магистр': 'Магистр',
               'Специалист': 'Специалист',
               'СПО': 'Среднее специальное образование',
               'Аспирантура': 'Подготовка кадров высшей квалификации'}

deps_dict = {
    'Управление аспирантуры и докторантуры': '000000269',
    'Институт заочного образования': '000001031',
    'Колледж высоких технологий': '000001052'
}


def get_dep_id_by_name(name):
    if name in deps_dict.keys():
        return deps_dict[name]
    dep = EduDepartment.objects.filter(name=name, freedate__isnull=True).first()
    if dep:
        return dep._id
    return name


def create_abiturient(filename):
    with open(filename, encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        for row in reader:
            student_share.create_abiturient(kod_1c=row['Код'],
                                            name=row['Имя'],
                                            surname=row['Фамилия'],
                                            patronymic=row['Отчество'],
                                            gender=row['Пол'],
                                            birthday_text=row['ДатаРождения'],
                                            doc_type_text=row['ТипДокументаУдостоверяющегоЛичность'],
                                            doc_series=row['СерияПаспорта'],
                                            doc_number=row['НомерПаспорта'],
                                            doc_date_text=row['ДатаВыдачи'],
                                            doc_dep=row['ОтделениеВыдачи'],
                                            citizen_text=row['Гражданство'],
                                            reg_address_obj=create_address('Регистрация', row),
                                            fact_address_obj=create_address('Проживание', row),
                                            email=row['Email'],
                                            uid=row['UID'],
                                            prevEduLevel_text=row['УровеньОбразования'],
                                            prevEduOrg=row['УчебноеЗаведение'],
                                            prevEduDocDateGet_text=row[
                                                'ДокументОбОбразованииДатаВыдачи'],
                                            prevEduDocType_text=row[
                                                'ДокументОбОбразованииТипДокумента'],
                                            prevEduDocSer=row['ДокументОбОбразованииСерия'],
                                            prevEduDocNum=row['ДокументОбОбразованииНомер'],
                                            original_doc=row['Оригинал'],  # 0/1
                                            abit_spec_code=row['СпециальностьКод'],
                                            abit_spec_name=row['СпециальностьНаименование'],
                                            abit_subspec_code=row['ПрофильКод'],
                                            abit_subspec_name=row['ПрофильНаименование'],
                                            abit_edu_form=row['ФормаОбучения'],
                                            edu_type=row['ПлатнаяФорма'],  # 0/1
                                            ent_doc_num=row['НомерПриказа'],
                                            ent_doc_date_text=row['ДатаПриказа'],
                                            foreign_lang_text=row['ИностранныйЯзык'],
                                            phone=row['Телефоны'],
                                            institute_id=get_dep_id_by_name(row['Факультет']))


def openAllAbiturient(request):
    if request.method == 'POST':
        create_abiturient('dekanat/abbitur/GET_ENROLLED_ASP_2018.csv')
        return JsonResponse({'status': "ok"})

    if request.method == 'GET':
        return render(request, 'abiturient.html', dict(abiturs=Student.objects.filter(status=0)))


def load_from_file(request):
    if request.method == 'POST':
        file = codecs.open('tmp/abiturient.csv', "wb")
        for c in request.FILES['file']:
            file.write(c)
        file.close()
        create_abiturient('tmp/abiturient.csv')
        return JsonResponse({'status': "ok"})


def check_abiturent_file(request):
    file = codecs.open('tmp/abiturient.csv', "wb")
    for c in request.FILES['file']:
        file.write(c)
    file.close()
    message = set()
    with open('tmp/abiturient.csv', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        for row in reader:
            uid = row['UID']
            ent_doc_num = row['НомерПриказа']
            ent_doc_date = datetime.strptime(row['ДатаПриказа'], '%d.%m.%Y').date()
            try:
                s = Student.objects.get(uid=uid, status__in=(1, 2, 3, 4, 5, 6, 7, 8))
                if s.abit_info.ent_doc_num != ent_doc_num:
                    message.add(
                        f'номер приказа не совпадает в бд {s.abit_info.ent_doc_num} - номер в файле {ent_doc_num}')
                elif s.abit_info.ent_doc_date != ent_doc_date:
                    message.add(
                        f'дата приказа {ent_doc_num} не совпадает в бд {s.abit_info.ent_doc_date} - номер в файле {ent_doc_date}')
            except ObjectDoesNotExist:
                pass
            except MultipleObjectsReturned:
                pass
    return HttpResponse('<br>'.join(message) + '<br><a href="/orders/">Приказы</a>')


def update_by_file(request):
    if request.method == 'POST':
        file = codecs.open('tmp/abiturient.csv', "wb")
        for c in request.FILES['file']:
            file.write(c)
        file.close()
        with open('tmp/abiturient.csv', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile, delimiter="|")
            for row in reader:
                uid = row['UID']
                ent_doc_num = row['НомерПриказа']
                ent_doc_date = datetime.strptime(row['ДатаПриказа'], '%d.%m.%Y').date()
                try:
                    s = Student.objects.get(uid=uid, status__in=(1, 2, 3, 4, 5, 6, 7, 8))
                    if s.abit_info.ent_doc_num != ent_doc_num or s.abit_info.ent_doc_date != ent_doc_date:
                        s.abit_info.ent_doc_num = ent_doc_num
                        s.abit_info.ent_doc_date = ent_doc_date
                        s.abit_info.save()
                except ObjectDoesNotExist:
                    pass
                except MultipleObjectsReturned:
                    pass
        return redirect('/orders/')
