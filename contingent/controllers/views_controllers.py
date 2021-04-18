from contingent.models import Student, Group, StudentHistory, Spec
from contingent.models.depart import Department


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
        child_deps = Department.objects.filter(dep=dep, is_producing=True, freedate=None)
        for child_dep in child_deps:
            all_deps.extend(self.__get_child_deps(child_dep))
        return all_deps

    def get_child_deps_edu(self, flag_free_date=True):
        deps = Department.objects.filter(dep=self.dep, is_producing=True)
        if flag_free_date:
            deps = deps.filter(freedate=None)
        return deps.order_by('sort_code', 'name')

    def get_student_query_set(self):
        deps = self.__get_child_deps(self.dep)
        return Student.objects.filter(group__dep__in=deps)

    def get_group_query_set(self):
        deps = self.__get_child_deps(self.dep)
        return Group.objects.filter(dep__in=deps)


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
