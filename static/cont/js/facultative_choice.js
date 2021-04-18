function on_load_table() {
    let row_count = $('#subjects_table tr').length - 4
    let $select_all_inputs = $('.select-all-input')
    $select_all_inputs.each(function (index) {
        let checked_count = $.grep($(`#subjects_table tr td:nth-child(${index + 2}) input`), function (input) {
            return $(input).prop('checked');
        })
        if (row_count === checked_count.length)
            $(this).prop('checked', true)
    })
    $select_all_inputs.click(function () {
        let val = $(this).prop('checked');
        let index = $(this).closest('tr').children().index($(this).parent());
        $(`#subjects_table tr td:nth-child(${index + 2}) input`).prop('checked', val);
    })


}

$(function () {
    let treeUtils = TreeUtils(3, false, on_load_table);
    treeUtils.createMenuTree(getTree(), 'tree', 2, true);
    $('#save_btn').click(function () {
        let form = $('#facultative_subjects_form');
        $.post(form.attr('action'), form.serialize(), function (data) {
            $('#contentDek').html(data);
            dekanat_modals.alertOK('сохранено');
        })
    });


})


