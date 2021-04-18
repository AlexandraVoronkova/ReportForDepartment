$(".student_tr").on("click", function () {
    let id_student = $(this).attr('id');
    $("table > tbody > tr").each(function () {
        $(this).css('backgroundColor', '');
    });
    $(this).css('backgroundColor', '#f5f5f5');
    $.ajax({
        url: "get_docs_student/" + id_student + '/',
        dataType: "html",
        success: function (data) {
            $("#id_cur_student").val(id_student);
            $("#table_student_doc").html(JSON.parse(data)["table_stud_docs"]);
            $("#other_doc_div").html('<h4 style="color:#2C3E50">Другие документы: </h4>' + JSON.parse(data)["other_docs"]);
        },
        error: function () {
            dekanat_modals.alertError('При загрузке произошла ошибка');
        }
    })
});

function get_id_selected_students() {
    let id_selected_students = [];
    $('.student_tr input:checked').each(function () {
        id_selected_students.push($(this).parent().parent().attr("id"))
    });
    return id_selected_students
}

$("#btn_print_act").on("click", function () {
    let id_check_students = get_id_selected_students();
    if (id_check_students.length > 0) {
        let data = {'id_check': JSON.stringify(id_check_students), 'expulsion_year': $('#history_year').val()};
        $('#form_send_data').val(JSON.stringify(data));
        $('#form_send').submit();
    }
    else {
        dekanat_modals.alertError("Выберите студентов");
    }
});

$("#btn_change_doc").on("click", function () {
    let id_check_students = get_id_selected_students();
    if (id_check_students.length > 0) {
        $('#id_students').val(JSON.stringify(id_check_students));
        $('#change_doc_modal').modal('show');
    }
    else {
        dekanat_modals.alertError("Выберите студента(ов) для изменения документов");
    }
});

$("#search-fio").on("keyup", function () {
    let table = $('#fio-students')[0];
    let regPhrase = new RegExp(($('#search-fio')).val(), 'i'); // i - игнорирование регистра
    let flag = false;
    for (let i = 1; i < table.rows.length; i++) {
        flag = false;
        flag = regPhrase.test(table.rows[i].cells[1].innerHTML);
        if (flag) {
            table.rows[i].style.display = "";
        }
        else {
            table.rows[i].style.display = "none"
        }
    }
});

function set_value_display_rows(value_display) {
    $('.check_group:input:checkbox:not(:checked)').each(function () {
        $($(this).parent().parent()).css('display', value_display);
    });
}

$("#show_selected").on("click", function () {
    if (this.checked === true) {
        $("#select_all_checkbox, #search-fio").attr('disabled', 'disabled').css('cursor', 'default');
        set_value_display_rows('none');
    }
    else {
        $("#select_all_checkbox, #search-fio").removeAttr('disabled');
        set_value_display_rows('');
    }
});

$('.check_group').click(function () {
    if ($('#show_selected')[0].checked) {
        $($(this).parent().parent()).css('display', 'none');
    }
});

function get_id_cur_student() {
    return $("#id_cur_student").val();
}
