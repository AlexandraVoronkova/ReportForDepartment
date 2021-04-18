# -*- coding: utf-8 -*-
from django.urls import path, re_path
from django.views.generic import RedirectView

from .views import contingent, custom_report

urlpatterns = [
    path('', RedirectView.as_view(url='contingent/')),
    path('contingent/', contingent.open_all_contingent),
    path('contingent/<int:dep_id>/<int:node_id>/<int:type>/<int:status>/',
         contingent.open_all_contingent),
    path('contingent/students/<int:dep_id>/<int:node_id>/<int:type>/<int:status>/',
         contingent.get_students_table_response),

    # для отображения на дату
    re_path(r'^contingent/(?P<date>[\d]{2}.[\d]{2}.[\d]{4})/$', contingent.open_all_contingent_by_date),
    re_path(
        r'^contingent/(?P<date>[\d]{2}.[\d]{2}.[\d]{4})/students/(?P<dep_id>\d+)/(?P<node_id>\d+)/(?P<type>\d+)/(?P<status>\d+)/$',
        contingent.get_students_table_by_date_response),

    # настраеваемый отчет
    path('contingent/get_custom_report_modal/', custom_report.get_report_modal),
    path(r'contingent/students/<int:dep_id>/<int:node_id>/<int:type>/<int:status>/print_custom_report/',
         custom_report.create_report),
    re_path(
        r'^contingent/(?P<date>[\d]{2}.[\d]{2}.[\d]{4})/students/(?P<dep_id>\d+)/(?P<node_id>\d+)/(?P<type>\d+)/(?P<status>\d+)/print_custom_report/',
        custom_report.create_report),

]
