from itertools import groupby

from .views_controllers import ViewDepartment


class DepartmentTree:
    """
        Класс для построения узлов дерева подразделений
    """

    def __init__(self, show_child=True):
        """
        :param show_child: показывать ли дочерние подразделения, такие как кафедры и РИМЦы
        """
        self.show_child = show_child

    def get_next_dep_level(self, dep, date):
        return []

    def dep_to_tree_point(self, dep):
        tree_dep = dict()
        tree_dep["text"] = str(dep)
        tree_dep['dbID'] = dep.id
        tree_dep['type'] = 0
        if hasattr(dep, 'edudepartment'):
            tree_dep['dep_type'] = 1 if not dep.is_main else 0
        else:
            tree_dep['dep_type'] = 0
        tree_dep['nodes'] = []
        return tree_dep

    def get_tree(self, dep, date=None):
        """
        Построение дерева
        :param dep: подразделение по которому строится дерево
        :param date: дата для отображения дерева согласно истории, если None, то показывать текущее состояние
        :return: дерево с подразделением dep
        """
        tree_dep = self.dep_to_tree_point(dep)
        view = ViewDepartment(dep)
        if date:
            child_deps = view.get_child_deps_edu_by_date(date)
        else:
            child_deps = view.get_child_deps_edu()
        if self.show_child and child_deps:
            for child in child_deps:
                tree_dep['nodes'].extend(self.get_tree(child, date))
        else:
            tree_dep['nodes'].extend(self.get_next_dep_level(dep, date))

        if not tree_dep['nodes']:
            tree_dep.pop('nodes', None)
        return [tree_dep]


class GroupTree:
    def get_next_group_level(self, group, date):
        pass

    def get_groups(self, dep, date):
        if date:
            groups = ViewDepartment(dep).get_all_groups_by_date(date)
        else:
            groups = ViewDepartment(dep).get_all_groups()
        return groups

    def create_group_node(self, groups, date):
        tree = []
        for group in groups:
            tree_group = dict()
            tree_group["text"] = '{} ({} курс)'.format(group.name_group, group.kurs)
            tree_group["type"] = 3
            tree_group["dbID"] = group.id
            nodes = self.get_next_group_level(group, date)
            if nodes:
                tree_group['nodes'] = nodes
            tree.append(tree_group)
        return tree


class GroupSpecTree(GroupTree, DepartmentTree):
    def edu_form_to_tree_point(self, edu_form):
        return {'text': edu_form.get_edu_form_display(), 'type': 8, 'dbID': edu_form.id, 'nodes': []}

    def spec_to_tree_point(self, spec):
        spec_tree = {}
        try:
            spec_tree["text"] = str(spec)
            spec_tree['type'] = 2
            spec_tree['dbID'] = spec.id
        except AttributeError:
            spec_tree["text"] = 'Ошибка: код и имя специальности не заданы'
        return spec_tree

    def group_by_spec(self, groups):
        specs = dict()
        for group in groups:
            if group.spec_group in specs:
                specs[group.spec_group].append(group)
            else:
                specs[group.spec_group] = [group]
        return specs

    def get_next_dep_level(self, dep, date):
        groups = self.get_groups(dep, date).order_by('spec_group__eduForm',
                                                     'spec_group__spec__code',
                                                     '-created_year', 'name_group')
        tree = []
        for edu_form, edu_form_groups in groupby(groups, key=lambda g: g.spec_group.eduForm):
            edu_form_tree = self.edu_form_to_tree_point(edu_form)
            for spec, spec_groups in self.group_by_spec(edu_form_groups).items():
                spec_tree = self.spec_to_tree_point(spec)
                group_tree = self.create_group_node(spec_groups, date)
                spec_tree['nodes'] = group_tree
                edu_form_tree['nodes'].append(spec_tree)
            tree.append(edu_form_tree)

        return tree


class GroupKafTree(GroupTree, DepartmentTree):
    def get_next_dep_level(self, dep, date):
        groups = self.get_groups(dep, date).order_by('-created_year', 'name_group')
        group_tree = self.create_group_node(groups, date)
        return group_tree
