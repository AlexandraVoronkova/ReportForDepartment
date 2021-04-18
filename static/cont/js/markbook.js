let treeUtils = TreeUtils(4);
let tree = JSON.parse(document.getElementById('tree-data').textContent);
treeUtils.createMenuTree(tree, 'student-tree', 2, true);
$(function (){
    $('select.bs-select-hidden, .bootstrap-select select.bs-select-hidden, select.selectpicker').css('display','none');
})

$('#status_select').change(function () {
    $('#status_form').submit()
})

$('#print_study_year_cert_btn').click(function () {
    let student = treeUtils.getSelectedNode('student-tree')[0];
    if (!student) {
        dekanat_modals.alertError('Выберите студента');
        return;
    }
    if ($('#cert_is_register').is(':checked') && (!$('#cert_reg_number').val() || !$('#sert_reg_date').val())) {
        dekanat_modals.alertError('Заполните регистрационный номер и дату выдачи');
        return;
    }
    $('#student_study_period_cert_input').val(student.dbID);
    $('#study_period_cert_form').submit();
});

function delete_item(item_id) {
    dekanat_modals.confirmYesNo('Вы действительно хотите удалить предмет из зачетки?', function (result) {
        if (result) {
            let node = treeUtils.getSelectedNode('student-tree')[0];
            $.post('/dekanat/markbook/' + node.dbID + '/delete_item/', {item_id: item_id}, function (data) {
                $('#contentDek').html(data);
            })
        }
    })
}

let choose_item_table;

function get_unchecked_items_modal() {
    let node = treeUtils.getSelectedNode('student-tree')[0];
    $.get('/dekanat/markbook/' + node.dbID + '/get_unchecked_items/', function (data) {
        $('#contentDek').append(data);
        choose_item_table = $('#choose_item_table').selecting_table({multiselect: false, selected_class: 'info'});
        $('#add_item_modal').modal('show');
    })
}

function add_item_click() {
    let node = treeUtils.getSelectedNode('student-tree')[0];
    let selected_subject = choose_item_table.get_selected()[0];
    $('#add_item_modal').modal('hide');
    $.post('/dekanat/markbook/' + node.dbID + '/add_item/', {subject_id: selected_subject}, function (data) {
        $('#contentDek').html(data);
    })
}

$('#print_avg_ref_btn').click(function () {
    let node = treeUtils.getSelectedNode('student-tree')[0];
    window.open('/dekanat/markbook/' + node.dbID + '/print_avg_ref/')
});

$('#print_debt_ref_btn').click(function () {
    let node = treeUtils.getSelectedNode('student-tree')[0];
    window.open('/dekanat/markbook/' + node.dbID + '/print_debt_ref/')
});

$('#print_markbook_btn').click(function () {
    let node = treeUtils.getSelectedNode('student-tree')[0];
    window.open('/dekanat/markbook/' + node.dbID + '/print_markbook/')
});

$('#print_accounting_btn').click(function () {
    let node = treeUtils.getSelectedNode('student-tree')[0];
    let semesters = $('#accounting_semesters').val()
    window.open('/dekanat/markbook/' + node.dbID + '/print_accounting/?semesters=' + semesters.join('&semesters='))
});