from dekanat.controllers.attestation.attestation_controller import AttestationGroupSpecTree, AttestationGroupKafTree
from dekanat.controllers.group_tree import GroupSpecTree, GroupKafTree
from dekanat.controllers.session.session_controller import SessionGroupSpecTree, SessionGroupKafTree
from dekanat.controllers.stipend_controller import StipendKafGroupTree, StipendSpecGroupTree
from dekanat.controllers.students_tree import StudentGroupKafTree, StudentGroupSpecTree
from dict_app.models_.depart import EduDepartment
from dict_app.models_.dict import DictEduYear

TREE_TYPES = {
    'contingent': {
        1: GroupSpecTree,
        2: GroupKafTree
    },
    'contingent_students': {
        1: StudentGroupSpecTree,
        2: StudentGroupKafTree
    },
    'attestation': {
        1: AttestationGroupSpecTree,
        2: AttestationGroupKafTree
    },
    'session': {
        1: SessionGroupSpecTree,
        2: SessionGroupKafTree
    },
    'stipend': {
        1: StipendSpecGroupTree,
        2: StipendKafGroupTree
    }
}


def get_institute_tree(subsystem, dep, date, view_type, edu_year_id, semestr_type):
    if not view_type or view_type == '0':
        view_type = dep.get_settings().treeview_type
    show_child = view_type == 2
    tree_creator = TREE_TYPES[subsystem][int(view_type)](show_child=show_child)
    edu_year = None
    if edu_year_id:
        edu_year = DictEduYear.objects.get(id=edu_year_id)
    return tree_creator.get_tree(dep, date, edu_year, semestr_type)


def get_bstu_tree_node(dep):
    tree_bstu = dict()
    tree_bstu["text"] = dep.name
    tree_bstu['dbID'] = dep.id
    tree_bstu['type'] = 0
    tree_bstu['nodes'] = []
    return tree_bstu


def get_tree(subsystem, dep, date=None, view_type=None, edu_year_id=None, semestr_type=None):
    if hasattr(dep, 'university'):
        tree_bstu = get_bstu_tree_node(dep)
        children = EduDepartment.objects.filter(type=1, dep=dep).order_by('name')
        for child in children:
            tree_bstu['nodes'].extend(get_institute_tree(subsystem, child, date, view_type, edu_year_id, semestr_type))
        return [tree_bstu]
    else:
        return get_institute_tree(subsystem, dep.edudepartment, date, view_type, edu_year_id, semestr_type)


def get_student_tree_class(dep, status):
    view_type = dep.get_field_settings('treeview_type')
    if view_type == 1:
        tree_class = StudentGroupSpecTree(show_child=False, status=status)
    else:
        tree_class = StudentGroupKafTree(show_child=True, status=status)

    return tree_class


def get_student_tree(dep, status):
    if hasattr(dep, 'university'):
        tree_bstu = get_bstu_tree_node(dep)
        children = EduDepartment.objects.filter(type=1, dep=dep).order_by('name')
        for child in children:
            tree_bstu['nodes'].extend(get_student_tree_class(child, status).get_tree(child))
        return [tree_bstu]
    else:
        return get_student_tree_class(dep, status).get_tree(dep)
