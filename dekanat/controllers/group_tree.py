from itertools import groupby

from dekanat.controllers.views_controllers import ViewDepartment
from dict_app.tree_dep_spec import DepartmentTree


class GroupTree:
    def get_next_group_level(self, group, date, edu_year=None, semestr_type=None):
        pass

    def get_groups(self, dep, date, edu_year, semester_type):
        if date:
            groups = ViewDepartment(dep).get_all_groups_by_date(date)
        else:
            groups = ViewDepartment(dep).get_all_groups()
        if edu_year:
            groups = groups.filter(created_year__lte=edu_year.start)
        return groups

    def create_group_node(self, groups, date, edu_year, semestr_type):
        tree = []
        for group in groups:
            tree_group = dict()
            tree_group["text"] = '{} ({} курс)'.format(group.name_group, group.kurs)
            tree_group["type"] = 3
            tree_group["dbID"] = group.id
            nodes = self.get_next_group_level(group, date, edu_year, semestr_type)
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

    def get_next_dep_level(self, dep, date, edu_year, semester_type):
        groups = self.get_groups(dep, date, edu_year, semester_type).order_by('spec_group__eduForm',
                                                                              'spec_group__spec__code',
                                                                              '-created_year', 'name_group')
        tree = []
        for edu_form, edu_form_groups in groupby(groups, key=lambda g: g.spec_group.eduForm):
            edu_form_tree = self.edu_form_to_tree_point(edu_form)
            for spec, spec_groups in self.group_by_spec(edu_form_groups).items():
                spec_tree = self.spec_to_tree_point(spec)
                group_tree = self.create_group_node(spec_groups, date, edu_year, semester_type)
                spec_tree['nodes'] = group_tree
                edu_form_tree['nodes'].append(spec_tree)
            tree.append(edu_form_tree)

        return tree


class GroupKafTree(GroupTree, DepartmentTree):
    def get_next_dep_level(self, dep, date, edu_year, semester_type):
        groups = self.get_groups(dep, date, edu_year, semester_type).order_by('-created_year', 'name_group')
        group_tree = self.create_group_node(groups, date, edu_year, semester_type)
        return group_tree
