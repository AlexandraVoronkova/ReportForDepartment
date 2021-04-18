function get_now_date_str() {
    let date_now = new Date();
    let day = ('0' + (date_now.getDate())).slice(-2);
    let month = ('0' + (date_now.getMonth() + 1)).slice(-2);
    return (day + '.' + month + '.' + date_now.getFullYear())
}

function clean_modal_doc() {
    $("#form-edit-stud-document").trigger("reset");
    $("#doc_type").selectpicker('refresh');
    $("#status_select").selectpicker('refresh');
    $("#sign_select").selectpicker('refresh');
    $("#depart_select").prop("disabled", true).selectpicker('refresh');
    $("#id_record").val("");
    $("#date_doc").val(get_now_date_str());
    $('#init_modal_stud_document').attr('cur_count_doc', 0);
}

function edit_tr_order(id_doc) {
    clean_modal_doc();
    $("#init_modal_stud_document").hide();
    $("#id_record").val(id_doc);
    $.ajax({
        url: '/dekanat/student/student_doc_dep/get_doc_student/',
        type: 'POST',
        data: {id_record: id_doc},
        success: function (data) {
            $("#doc_type").val(data.type_doc).selectpicker('refresh');
            $("#status_select").val(data.status).selectpicker('refresh');
            $("#series_doc").val(data.series);
            $("#number_doc").val(data.number);
            if (data.sign == true) {
                $("#sign_select").val("True").selectpicker('refresh');
            }
            else if (data.sign == false) {
                $("#sign_select").val("False").selectpicker('refresh');
            }
            $("#date_doc").val(get_now_date_str());
            let depart_select = $("#depart_select");
            depart_select.val(data.location);
            if (data.status == 1) {
                depart_select.prop("disabled", false);
            }
            else {
                depart_select.prop("disabled", true);
            }
            depart_select.selectpicker('refresh');
            $('#edit_doc_student_modal').modal('show');
        }
    });
}

function del_doc(id_doc) {
    dekanat_modals.confirmYesNo("Удалить строку?", function (result) {
        if (result) {
            $.ajax({
                type: "POST",
                url: '/dekanat/student/student_doc_dep/delete_doc/',
                data: {
                    'id_record': id_doc
                },
                success: function (data) {
                    window.location.reload();
                }
            });
        }
    })
}

function create_record_doc(cur_count_doc) {
    clean_modal_doc();
    $("#init_modal_stud_document").show();
    $('#init_modal_stud_document').attr('cur_count_doc', cur_count_doc);
    $('#edit_doc_student_modal').modal('show');
}

function getValue(value) {
    var sel = $("#depart_select");
    if (value == 1) {
        sel.prop("disabled", false);
    }
    else {
        sel.prop("disabled", true);
    }
    sel.selectpicker('refresh');
}

$("#save_modal_stud_document").on('click', function () {
    let id_student = get_id_cur_student();
    $.ajax({
        url: '/dekanat/student/student_doc_dep/student_documents/?id=' + id_student,
        type: 'POST',
        data: $('#form-edit-stud-document').serialize(),
        success: function (data) {
            window.location.reload();
        }
    })
});

function init_stud_documents() {
    let id_student_url = get_id_cur_student();
    $.ajax({
        url: '/dekanat/student/student_doc_dep/init_pers_doc/?id=' + id_student_url,
        type: 'POST',
        success: function (data) {
            window.location.reload();
        }
    })
}

$("#init_modal_stud_document").on('click', function () {
    var count_docs = $(this).attr('cur_count_doc');
    if (count_docs > 0) {
        dekanat_modals.confirmYesNo("Документы студента сформированы.<br> Удалить существуюшие и сформировать заново?", function (result) {
            if (result) {
                init_stud_documents()
            }
        })
    }
    else {
        init_stud_documents()
    }
});
