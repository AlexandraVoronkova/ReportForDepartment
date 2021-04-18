$('#btn_add_relstive').on('click', function () {
    $("#form-edit-relative").trigger("reset");
    $("#relative_type_select").selectpicker('refresh');
    $('#edit_relative_student_modal').modal('show');
});

function edit_relative(id_relative) {
    $("#form-edit-relative").trigger("reset");
    $("#relative_type_select").selectpicker('refresh');
    $("#relative_id").val(id_relative);
    $(".input_phone").removeClass('error_input');
    $(".input_email").removeClass('error_input');
    $.ajax({
        url: '/dekanat/student/get_relative_student/',
        type: 'POST',
        data: {id_relative: id_relative},
        success: function (data) {
            let $relative_type_select = $("#relative_type_select");
            $relative_type_select.val(data.type - 1);
            $relative_type_select.selectpicker('refresh');

            $("#surname_relative").val(data.surname);
            $("#name_relative").val(data.name);
            $("#patronymic_relative").val(data.patronymic);
            $("#address_relative").val(data.address);
            /*$("#address_kladr").val(data.address_kladr);*/
            $("#work_place").val(data.work_place);
            $("#post").val(data.post);
            $("#phone_relative").val(data.phone);
            $("#email_relative").val(data.email);
            $("#birthday_relative").val(data.birthday);
            if (data.sms == true) {
                $('#is_sms').prop('checked', true)
            }
            else {
                $('#is_sms').prop('checked', false)
            }

            $('#edit_relative_student_modal').modal('show');
        }
    });
}

$('.edit-relative-class').on('dblclick', function () {
    let tr_group = $(this);
    let id_relative = $(tr_group.children()[0]).text();
    edit_relative(id_relative)
});

$('.btn-edit-tr-relative').on('click', function () {
    let id_relative = $(this).attr("relatid");
    edit_relative(id_relative)
});

function save_relativ_btn_click(student_id) {
    let check1 = regex_phone($("#phone_relative"));
    let check2 = regex_mail($("#email_relative"));
    if ($('#surname_relative').val() && $('#name_relative').val() && $('#relative_type_select').val() &&
        $('#phone_relative').val()) {
        if (check1 && check2) {
            $.ajax({
                url: '/dekanat/student/redact_relative_student/' + student_id + '/',
                type: 'POST',
                data: $('#form-edit-relative').serialize(),
                success: function (data) {
                    window.location.reload();
                }
            })
        }
    }
    else {
        dekanat_modals.alertError("Не все обязательные поля заполнены!");
    }
}

$('#address_relative').kladr({oneString: true});

$('.input_phone').focusout(function () {
    regex_phone($(this));
});

$('.input_email').focusout(function () {
    regex_mail($(this));
});

function regex_phone(element) {
    let phone = element.val();
    let phone_regex = /[a-zа-я]{1,}/i;
    if (phone.length > 0 && phone_regex.test(phone) == true) {
        element.addClass('error_input');
        return false
    }
    else {
        element.removeClass('error_input');
        return true
    }
}

function regex_mail(element) {
    let email = element.val();
    let mail_regex = /^[A-Z0-9._%+-]+@[A-Z0-9-]+.+.[A-Z]{2,4}$/i;
    if (email.length > 0 && mail_regex.test(email) == false) {
        element.addClass('error_input');
        return false
    }
    else {
        element.removeClass('error_input');
        return true
    }
}