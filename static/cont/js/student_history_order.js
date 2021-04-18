function clean_modal_history_order() {
    $("#form-edit-historyorder").trigger("reset");
    $("#order_type_select").selectpicker('refresh');
    $("#depart_select").selectpicker('refresh');
    $("#id_history_order").val("");
}

$(".btn-edit-tr-order").on('click', function () {
    let id_order = $(this).attr("orderid");
    clean_modal_history_order();
    $("#id_history_order").val(id_order);
    $.ajax({
        url: '/dekanat/student/get_history_order_student/',
        type: 'POST',
        data: {id_order: id_order},
        success: function (data) {
            let $order_type_select = $("#order_type_select");
            $order_type_select.val(data.type_order);
            $order_type_select.selectpicker('refresh');

            let $depart_select = $("#depart_select");
            $depart_select.val(data.department);
            $depart_select.selectpicker('refresh');

            $("#number_order").val(data.number);
            $("#date_order").val(data.date);
            $('#edit_order_student_modal').modal('show');
        }
    });
});

$("#btn-create-order").on('click', function () {
    clean_modal_history_order();
    $('#edit_order_student_modal').modal('show');
});

$(".btn-del-tr-order").on('click', function () {
    let id_order = $(this).attr("orderid");
    dekanat_modals.confirmYesNo("Удалить приказ?", function (result) {
        if (result) {
            $.ajax({
                type: "POST",
                url: '/dekanat/student/delete_historyorder/',
                data: {
                    'id_order': id_order
                },
                success: function (data) {
                    //$("#tbody_historyorder").html(data);
                    window.location.reload();
                }
            });
        }
    });
});