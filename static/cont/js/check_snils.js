function check_snils(snils) {
    var result = false;
    if (snils.length !== 11) {
        dekanat_modals.alertError("СНИЛС может состоять только из 11 цифр");
    }
    else {
        var sum = 0;
        for (var i = 0; i < 9; i++) {
            sum += Number(snils[i]) * (9 - i);
        }
        var check_digit = 0;
        if (sum < 100) {
            check_digit = sum;
        }
        else if (sum > 101) {
            check_digit = Number(sum % 101);
            if ((check_digit === 100) || (check_digit === 101)) {
                check_digit = 0;
            }
        }
        if (check_digit === Number(snils.slice(-2))) {
            result = true;
        }
        else {
            dekanat_modals.alertError("Введён некорректный номер СНИЛС");
        }
    }
    return result
}

$(function () {
    $("#snils_number").mask("999-999-999 99");
});

$("#btn-save-doc").on('click', function () {
    let snils = $('#snils_number').val();
    snils = snils.replace(/\D+/g, "");
    if (check_snils(snils)) {
        let form = $('#saveDoc');
        form.submit();
    }
});
