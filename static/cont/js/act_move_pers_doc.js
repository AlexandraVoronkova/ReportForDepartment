function get_id_selected_rows() {
    let id_selected_row = [];
    $('.checkbox_order:input:checkbox:checked').each(function () {
        id_selected_row.push($(this).attr('id'))
    });
    return id_selected_row
}

$(".checkbox_order").on("click", function () {
    let list_id = get_id_selected_rows();
    $.ajax({
        url: "get_students/",
        type: "GET",
        dataType: "html",
        data: {'orders_id': JSON.stringify(list_id)},
        success: function (data) {
            data = JSON.parse(data)['data'];
            let tbody_students = $('#tbody_fio_students').empty();
            for (let i = 0; i < data.length; i++) {
                tbody_students.append($('<tr><td>' + data[i].group + '</td><td>' + data[i].student + '</td></tr>'))
            }
        },
        error: function () {
            dekanat_modals.alertError('При загрузке произошла ошибка');
        }
    })
});

$(".order_tr").on("click", function (e) {
    if (!$(e.target).is(':checkbox')) {
        $(this).find(":checkbox").click();
    }
});

$("#btn_print_act").on("click", function () {
    let id_check_orders = get_id_selected_rows();
    if (id_check_orders.length > 0) {
        $('#form_send_data').val(JSON.stringify(id_check_orders));
        $('#print_act_modal').modal('show');
    }
    else {
        dekanat_modals.alertError("Выберите приказы");
    }
});
