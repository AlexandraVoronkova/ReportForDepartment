let $tree = $('#tree');
let $table = $('#contingent_table').selecting_table({multiselect: true});

let dp = $('#historyDate').datepicker().data('datepicker');
if (getDate())
    dp.selectDate(new Date(getDate()));
else
    dp.selectDate(new Date());

function get_current_url(node) {
    if (!node)
        node = $tree.treeview('getSelected', 1)[0];
    if (!node)
        node = $tree.treeview('getNode', 0);

    let status = $('#status_select').val();
    let institute_node = node;
    while (institute_node.type != 0) {
        institute_node = $tree.treeview('getParent', institute_node)
    }

    return 'students/' + institute_node.dbID + '/' + node.dbID + '/' + node.type + '/' + status + '/'

}

$tree.treeview({
    data: getTree(),
    backColor: '#d6e2e2',
    expandIcon: 'glyphicon glyphicon-chevron-down',
    collapseIcon: 'glyphicon glyphicon-chevron-up',
    selectedBackColor: '#335d73',
    onhoverColor: '#99bdb9'
});

let filter_inputs = {
    text: '<input class="form-control student_filter_input">',
    select: '<select class="form-control student_filter_input selectpicker" multiple title="Фильтр не выбран" data-actions-box="true" data-deselect-all-text="Снять все" data-select-all-text="Выбрать все">',
    date: '<input class="form-control student_filter_input datepicker-here" data-position="left bottom" type="text" data-range="true" data-multiple-dates-separator=" - " autocomplete="off">',
    bool: '<input class="student_filter_input" type="checkbox">'
};

function add_select_options(select, options) {
    options.forEach(function (opt, index) {
        let option = $('<option></option>').attr('value', opt.value).text(opt.label);
        select.append(option);
    })

}

function create_table_header() {
    let $table = $('#contingent_table');
    let columns = getFields();
    let thead = $('<thead></thead>');

    let tr = $('<tr></tr>');
    columns.forEach(function (col, index, array) {
        tr.append($('<th>' + col.label + '</th>'))
    });
    thead.append(tr);

    tr = $('<tr></tr>');
    columns.forEach(function (col, index, array) {
        let input = $(filter_inputs[col.filter_type]).attr('name', col.json_field);
        if (col.filter_type === 'select')
            add_select_options(input, col.options);
        tr.append($('<th></th>').append(input))
    });
    thead.append(tr);

    $table.append(thead);
}


function create_table_body(students_json) {
    let $table_body = $('#contingent_table_body');
    $table_body.html('');
    let columns = getFields();

    students_json.forEach(function (student, index) {
        let tr = $('<tr></tr>').data('id', student.id).on('dblclick', function (event) {
            window.open('/dekanat/student/' + student.id + '/')
        });
        columns.forEach(function (col, index) {
            let cell = student[col['json_field']];
            if (cell == null) cell = "";
            tr.append($('<td></td>').html(cell));
        });

        $table_body.append(tr);
    })
}


function create_choose_field_checkbox(col, index) {
    let div = $('<div class="checkbox-dek"></div>');
    let label = $('<label></label>');
    let input = $('<input type="checkbox" name="contingent_columns">').attr('value', index);
    if (!col.hidden) {
        input.prop('checked', true);
    }
    label.append(input);
    label.append($('<span class="cr"><i class="cr-icon glyphicon glyphicon-ok"></i></span>'));
    label.append(col.label);
    div.append(label);
    return div;

}

function create_modal_choose_fields() {
    let columns = getFields();
    let modal_body = $('#choose_columns_modal .modal-body');
    columns.forEach(function (col, index, array) {
        let checkbox = create_choose_field_checkbox(col, index + 1); // index + 1, потому что в сss нумерация с 1
        modal_body.append(checkbox);
    });
}


function load_students(url, page, filter) {
    let data = {};
    if (page) {
        data['page'] = page
    }
    if (filter) {
        data['filter'] = JSON.stringify(filter)
    }
    $.ajax({
        url: url,
        data: data,
        dataType: "json",
        success: function (data) {
            create_table_body(JSON.parse(data.students));
            $('#pagination').html(data.pagination);
            show_hide_columns();
        },
        error: function () {
            dekanat_modals.alertError('При загрузке произошла ошибка');
        }
    })
}

function show_hide_columns() {
    let checkbokces = $('input[name="contingent_columns"]');
    $('#contingent_table th, #contingent_table td').hide();
    let visible_columns = checkbokces.filter(':checked').serializeArray().map(el => el.value);
    visible_columns.forEach(function (val, index) {
        $('#contingent_table th:nth-child(' + val + '), #contingent_table td:nth-child(' + val + ')').show();
    });
}

create_table_header();
create_table_body(getStudents());
create_modal_choose_fields();
show_hide_columns();

function get_filter_data() {
    let filter_data = $('.student_filter_input:input').map(function () {
        let el = $(this);
        let type;
        if (el.hasClass('selectpicker')) {
            type = 'select'
        } else if (el.hasClass('datepicker-here')) {
            type = 'date'
        } else if (el.attr('type') === 'checkbox') {
            type = 'bool';
            return {name: el.attr('name'), value: el.is(':checked'), type: type}
        } else
            type = 'text';
        return {name: el.attr('name'), value: el.val(), type: type}
    }).get();
    filter_data = filter_data.filter(param => (param['value'].length !== 0 && param['value'] !== false));
    return filter_data
}

function clear_filters() {
    $('.student_filter_input:input').val('');
    $('.student_filter_input:checked').prop('checked', false);
    $('select.student_filter_input').selectpicker("refresh");
    filter_students();
}

$('#clear_filter_btn').click(function () {
    clear_filters();
});

$tree.on('nodeSelected', function (event, node) {
    clear_filters();
    load_students(get_current_url(node));
});

function get_contingent_page(url, page) {
    let filter_data = get_filter_data();
    load_students(get_current_url(), page, filter_data);
}


function filter_students() {
    load_students(get_current_url(), 1, get_filter_data());
}

$('.student_filter_input').change(function () {
    filter_students()
});

$('.student_filter_input.datepicker-here').datepicker({
    onSelect: function (formattedDate, date, inst) {
        filter_students();
    }
});


$('#status_select').on('change', function () {
    let status = $(this).val();
    load_students(get_current_url());
});

$('#select_all').click(function () {
    $table.select_all();
});

$('#unselect_all').click(function () {
    $table.unselect_all();
});


$('#show_hide_columns_btn').click(function () {
    show_hide_columns();
    $('#choose_columns_modal').modal('hide');
});


$('#history_btn').click(function (ev) {
    window.location.href = '/dekanat/contingent/' + $('#historyDate').val();
});

$('#view_type_switch input').click(function () {
    window.location.href = window.location.pathname + '?viewtype=' + $(this).val()
});

function print_report(report_type) {
    let url = get_current_url() + report_type + '/';
    if ($table.selected_all) {
        let filter = get_filter_data();
        window.open(url + '?filter=' + JSON.stringify(filter));
    } else {
        let students = $table.get_selected();
        if (students.length > 0)
            window.open(url + '?students=' + students.join('&students='));
    }
}

$('#print_ref_btn').click(function () {
    let student = $table.get_selected()[0];
    if (!student) {
        dekanat_modals.alertError('Выберите студента');
        return;
    }
    $('#student_ref_input').val(student);
    let $form = $('#print_reference_form');
    if ($('#save_docx').is(':checked')) {
        $form.attr('action', "/dekanat/contingent/students/print_reference_docx/")
    }
    $form.submit();
});

$('#print_bypass_btn').click(function () {
    print_report('print_bypass');
});

$('#print_milref_btn').click(function () {
    print_report('print_military_ref');
});


function toggle_readonly(selector) {
    let input = $(selector);
    input.prop('disabled', !input.prop('disabled'));
}

$('#is_change_spec_checkbox').change(function () {
    toggle_readonly('#mil_ref_spec')
});
$('#is_change_kurs_checkbox').change(function () {
    toggle_readonly('#mil_ref_kurs')
});

$('#milref_editor_modal').on('shown.bs.modal', function () {
    let student = $table.get_selected()[0];
    if (!student) {
        dekanat_modals.alertError('Выберите студента');
        return;
    }
    $('#student_milref_input').val(student);
});

$('#print_mil_ref_btn').click(function () {
    let url = get_current_url() + 'print_military_ref/';
    if ($table.selected_all) {
        let filter = get_filter_data();
        url = url + '?filter=' + JSON.stringify(filter);
    } else {
        let students = $table.get_selected();
        if (students.length > 0)
            url = url + '?students=' + students.join('&students=');
    }
    let params = $('#mil_ref_form').serialize()
    url += '&' + params
    // if ($('#is_change_spec_checkbox').is(':checked')) {
    //     url = url + '&mil_ref_spec=' + $('#mil_ref_spec').val();
    // }
    // if ($('#is_change_kurs_checkbox').is(':checked')) {
    //     url = url + '&mil_ref_kurs=' + $('#mil_ref_kurs').val();
    // }
    window.open(url);
});


$('#print_custom_report').click(function () {
    let modal = $('#custom_report_modal');
    if (modal.length > 0) {
        modal.modal('show');
        return;
    }
    $.ajax({
        url: "/dekanat/contingent/get_custom_report_modal/",
        dataType: "html",
        success: function (data) {
            $(data).appendTo('body');
            $('#custom_report_modal').modal('show');
        },
        error: function () {
            dekanat_modals.alertError('При загрузке произошла ошибка');
        }
    })
});

$('#print_file_irbis').click(function () {
    let url = get_current_url() + 'get_file_irbis/?';
    if ($table.selected_all)
        url = url + 'filter=' + JSON.stringify(get_filter_data());
    else {
        url = url + 'students=' + $table.get_selected(0).join('&students=');
    }
    window.open(url);
});

$('#export_word').click(function () {
    let url = get_current_url() + 'print_mil_ref_doc/';
    if ($table.selected_all) {
        let filter = get_filter_data();
        url = url + '?filter=' + JSON.stringify(filter);
    } else {
        let students = $table.get_selected();
        if (students.length > 0)
            url = url + '?students=' + students.join('&students=')
    }
    window.open(url);
});

$('#export_excel_btn').click(function () {
    let columns = getFields();
    let checkbokces = $('input[name="contingent_columns"]');
    let visible_columns_indexes = checkbokces.filter(':checked').serializeArray().map(el => el.value);
    let report_columns = [];
    for (let i in visible_columns_indexes) {
        report_columns.push(columns[visible_columns_indexes[i] - 1]['json_field'])
    }
    let url = get_current_url() + 'export_excel/';
    if ($table.selected_all) {
        let filter = get_filter_data();
        url = url + '?filter=' + JSON.stringify(filter);
    } else {
        let students = $table.get_selected();
        if (students.length > 0)
            url = url + '?students=' + students.join('&students=')
    }
    let is_report_fio_concat = $('#is_report_fio_concat').is(':checked')
    url = url + '&columns=' + report_columns.join('&columns=');
    if (is_report_fio_concat)
        url = url + '&fio_concat=on'
    window.open(url);
});

function create_xlsx_report(action, deny_bstu) {
    let node = $tree.treeview('getSelected', 1)[0];
    if (!node || node.type != 0 || (deny_bstu && node.dep_type != 1)) {
        dekanat_modals.alertError('Выберите институт');
        return;
    }
    $('#report_dep_input').val(node.dbID);
    $('#report_form').prop('action', action);
    $('#report_modal').modal('show');
}

$('#movement_report_btn').click(function () {
    create_xlsx_report('movement_report/', true);
});
$('#dismissed_report_btn').click(function () {
    create_xlsx_report('dismissed_transfered_report/');
});
$('#report_form').submit(function (e) {
    $('#report_modal').modal('toggle');
    return true;
});

$('#print_group_list').click(function () {
    let node = $tree.treeview('getSelected', 1)[0];
    if (!node || node.type != 3) {
        dekanat_modals.alertError('Выберите группу');
        return;
    }
    window.open('/dekanat/contingent/print_group_list/' + node.dbID)
});
