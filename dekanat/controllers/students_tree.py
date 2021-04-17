from dekanat.controllers.group_tree import GroupKafTree, GroupSpecTree
from dekanat.controllers.views_controllers import ViewGroup


class StudentTree:
    def __init__(self, show_child=False, status=1):
        self.status = status
        super().__init__(show_child)

    def get_next_student_level(self, date, student):
        pass

    def get_student_node(self, students, date):
        tree = []
        for student in students:
            tree_student = dict()
            tree_student["text"] = student.short_name()
            tree_student["type"] = 4
            tree_student["dbID"] = student.id
            nodes = self.get_next_student_level(date, student)
            if nodes:
                tree_student['nodes'] = nodes
            tree.append(tree_student)
        return tree

    def get_next_group_level(self, group, date, edu_year=None, semestr_number=None):
        if date:
            students = ViewGroup(group).get_all_students_in_history(date=date, status=self.status)
        else:
            students = ViewGroup(group).get_all_student(status=self.status)
        return self.get_student_node(students, date)


class StudentGroupKafTree(StudentTree, GroupKafTree):
    pass


class StudentGroupSpecTree(StudentTree, GroupSpecTree):
    pass
