from django.contrib import admin
from dekanat.models import *


class StudentAdmin(admin.ModelAdmin):
    list_display = ("uid", "name", 'surname', 'patronymic', 'status', 'edu_type', 'zcode', 'kurs', 'group', 'plan')
    exclude = ('info', 'person_doc', 'docs', 'bank_details', 'prev_edu', 'gak_info', 'hostel', 'mil_info', 'job',
               'abit_info')
    readonly_fields = 'exclude_learn_subjects',


admin.site.register(Group)
admin.site.register(Student, StudentAdmin)
admin.site.register(StudentInfo)
admin.site.register(StudentHostel)
admin.site.register(StudentAbitInfo)
admin.site.register(StudentMilitaryControl)
admin.site.register(DocStudPersDep)

admin.site.register(Attestation)
admin.site.register(AttestationAspirantCheckDict)
admin.site.register(AttestationItemAspirant)

admin.site.register(Session)
admin.site.register(SessionSubjectControl)
admin.site.register(SessionScorecard)
admin.site.register(SessionScorecardItem)
admin.site.register(GroupStipend)
admin.site.register(Reference)
