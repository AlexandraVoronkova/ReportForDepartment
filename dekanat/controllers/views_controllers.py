from django.db.models import Q

from dekanat.models.group import Group
from dekanat.models.student import Student
from dict_app.models_.depart import EduDepartment
from edu_plans.models.plan_dict import SubjectType
from edu_plans.models.spec import Spec, DictSpec
from history_app.controllers.student_controller import get_student_state
from history_app.models import StudentHistory


class ViewBase:
    """
        Абстрактный класс для выбора студентов и групп по объектам
    """

    def get_student_query_set(self):
        """
        Абстрактный метод для выбора студентов по объекту
        :return: QuerySet по Student
        """
        return Student.objects.none()

    def get_all_student(self, status=1, filter_kwargs=None):
        """
        Находит список студентов по объектам
        :param filter_kwargs:
        :param status:
        :return: список студентов
        """
        if type(status) is int:
            status = (status,)

        if status[0] == 100:
            status = (1, 2, 3, 4, 5, 5, 6, 7, 8)

        students = self.get_student_query_set().order_by('surname', 'name').filter(status__in=status)
        if filter_kwargs:
            students = students.filter(filter_kwargs)
        return students

    def get_group_query_set(self):
        """
        Абстрактный метод для выбора групп по объекту
        :return: QuerySet по Group
        """
        return Group.objects.none()

    def get_all_groups(self, flag_free_date=True):
        """
        Находит список групп по объектам
        :param flag_free_date: Учитывать ли наличие записи в freeDateGroup
        :return: список групп
        """
        groups = self.get_group_query_set()
        if flag_free_date:
            return groups.filter(free_date_group=None)
        return groups

    def get_all_groups_empty(self, flag_free_date=False):
        """
        Находит список пустых групп по объектам
        :param flag_free_date: Учитывать ли наличие записи в freeDateGroup
        :return: список пустых групп
        """
        groups = self.get_all_groups(flag_free_date)
        empty_groups = []

        for group in groups:
            if not Student.objects.filter(group=group, status=1).exists():
                empty_groups.append(group)
        return empty_groups

    def get_all_groups_by_date(self, date):
        """
        Находит список групп по объектам
        :param date: дата в истории
        :return: список групп
        """
        groups = self.get_group_query_set().filter(created_date_group__lte=date)
        groups = groups.filter(free_date_group=None) | groups.filter(free_date_group__gt=date)
        return groups.order_by('name_group')

    def get_all_students_in_history(self, date, status=(1,), filter_no_hist=None, filter_history=None):
        """
        Находит StudentHistory на определенную дату с заданными фильтрами
        :param date: дата
        :param status: статус студента на дату
        :param filter_no_hist: фильтры которые не зависят от истории
        :param filter_history: фильтры которые зависят от истории
        :return: QuerySet StudentHistory
        """
        if type(status) is int:
            status = (status,)

        if status[0] == 100:
            status = (1, 2, 3, 4, 5, 5, 6, 7, 8)

        groups_id = self.get_all_groups_by_date(date)

        hist_ids = StudentHistory.objects.filter(date__lte=date) \
            .order_by('student__id', '-date', '-id') \
            .distinct('student__id') \
            .values_list('id', flat=True)
        if filter_no_hist:
            students = Student.objects.filter(filter_no_hist)
            hist_ids = hist_ids.filter(student__in=students)
        students = StudentHistory.objects.filter(id__in=hist_ids, status__in=status, group__in=groups_id)
        if filter_history:
            students = students.filter(filter_history)
        return students.order_by('student__surname', 'student__name')


class ViewGroup(ViewBase):
    def __init__(self, group):
        self.group = group

    def get_student_query_set(self):
        return Student.objects.filter(group=self.group).order_by('surname', 'name')

    def get_all_groups_by_date(self, date):
        return [self.group]

    def get_student_learn_subject(self, plan_subject, date=None):
        """
        Возвращает студентов группы, которые изучают заданный предмет
        :param plan_subject: предмет плана
        :param date: дата в истории
        :return: Список студентов или список студентов в истории
        """
        q = Q(plan=plan_subject.plan) | Q(plan__parent=plan_subject.plan)
        if not date:
            students = self.get_student_query_set().filter(status=1).filter(q)
            if plan_subject.type not in SubjectType.main_subjects():
                students = (students.filter(elective_subjects=plan_subject) |
                            students.filter(facultative_subjects=plan_subject))
            return students
        else:
            n_h = Q()
            if plan_subject.type != SubjectType.MAIN_SUBJECT:
                n_h = Q(elective_subjects=plan_subject) | Q(facultative_subjects=plan_subject)
            students_history = self.get_all_students_in_history(date, status=1, filter_no_hist=n_h, filter_history=q)
            students = []
            for student in students_history:
                students.append(get_student_state(student.student, student))
            return list(students)


class ViewDepartment(ViewBase):
    def __init__(self, dep):
        if hasattr(dep, 'edudepartment'):
            self.dep = dep.edudepartment
        else:
            self.dep = dep

    def __get_child_deps(self, dep):
        all_deps = []
        if hasattr(dep, 'edudepartment'):
            all_deps.append(dep)
        child_deps = EduDepartment.objects.filter(dep=dep, is_producing=True, freedate=None)
        for child_dep in child_deps:
            all_deps.extend(self.__get_child_deps(child_dep))
        return all_deps

    def get_child_deps_edu(self, flag_free_date=True):
        deps = EduDepartment.objects.filter(dep=self.dep, is_producing=True)
        if flag_free_date:
            deps = deps.filter(freedate=None)
        return deps.order_by('sort_code', 'name')

    def get_student_query_set(self):
        deps = self.__get_child_deps(self.dep)
        return Student.objects.filter(group__dep__in=deps)

    def get_group_query_set(self):
        deps = self.__get_child_deps(self.dep)
        return Group.objects.filter(dep__in=deps)

    def get_all_spec(self):
        deps = self.get_child_deps_edu() + [self.dep]
        return list(Spec.objects.filter(dep__in=deps))

    def get_available_dict_spec(self):
        settings = self.dep.get_settings()
        levels = settings.get_available_levels()
        return DictSpec.objects.filter(level__level__in=levels)

    def get_avialable_specs(self):
        """
        Возвращает список направлений доступных подразделению
        :return:
        """
        settings = self.dep.get_settings()
        specs_type = settings.plan_available_type
        specs = Spec.objects.filter(spec__parent__isnull=True)  # выбор только направлений
        levels = settings.get_available_levels()
        if specs_type == 1:
            # выбор очных направлений привязанных к подразделению dep в соответствии с level
            return specs.filter(dep=self.dep, eduForm__edu_form=1, spec__level__level__in=levels)
        elif specs_type == 2:
            # выбор всех заочных направлений в соответсвии с level
            return specs.filter(eduForm__edu_form__in=[2, 3, 4], spec__level__level__in=levels)
        elif specs_type == 3:  # выбор всех направлений по level
            return specs.filter(spec__level__level__in=levels)

    def get_avialable_abiturients(self):
        settings = self.dep.get_settings()
        # abit_type = settings.available_abiturient
        dep = self.dep
        # if abit_type == 2:  # для института дистанционки
        #     dep = EduDepartment.objects.get(oldDekanatId=1975)  # необходимо показать абитуриентов заочки #todo потом вернуть в нормальное состояние

        zaoch_dep = EduDepartment.objects.get(oldDekanatId=1975)
        return Student.objects.filter(status=0, abit_info__abit_dep__in=[dep, zaoch_dep]).exclude(abit_info=None)

    # Функции для просмотра истории
    def get_child_deps_edu_by_date(self, date):
        deps = EduDepartment.objects.filter(dep=self.dep, is_producing=True)
        deps = deps.filter(freedate=None) | deps.filter(freedate__gte=date)
        return list(deps.order_by('name'))


class ViewSpec(ViewBase):
    def __init__(self, spec, curr_dep):
        self.spec = spec
        self.curr_dep = curr_dep

    def get_student_query_set(self):
        students = ViewDepartment(self.curr_dep).get_all_student()
        specs = [self.spec]
        specs.extend(Spec.objects.filter(spec__parent=self.spec.spec))
        return students.filter(group__spec_group__in=specs)

    def get_group_query_set(self):
        specs = [self.spec]
        specs.extend(Spec.objects.filter(spec__parent=self.spec.spec))
        return Group.objects.filter(spec_group__in=specs)
