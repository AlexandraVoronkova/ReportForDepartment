function download_abiturient(url, data) {
    $.ajax({
        type: "POST",
        url: "/dekanat/abiturient/",
        success: function (data) {
            if (data.status == 'ok') {
                dekanat_modals.alert('Загружено', 'ok')
            }
            else {
                dekanat_modals.alertError("Ошибка при загрузке");
            }
        },
        error: function () {
            dekanat_modals.alertError("Ошибка при загрузке");
        }

    });
}


function ajax_load_data_from_file(url, formData) {
    $.ajax({
        url: url,
        type: 'POST',
        data: formData,
        success: function (data) {
            if (data.status === 'ok') {
                dekanat_modals.alertOK('Загружено');
                console.log('message:' + data.message)
            }
            else {
                dekanat_modals.alertError("Ошибка при загрузке");
            }
        },
        fail: function () {
            dekanat_modals.alertError("Ошибка при загрузке");
        },
        cache: false,
        contentType: false,
        processData: false
    });
}


function download_abiturient_from_file() {
    var formData = new FormData(document.getElementById('abitfileForm'));
    ajax_load_data_from_file("/dekanat/abiturient/load_file/", formData)
}


function load_employer_from_file() {
    var formData = new FormData(document.getElementById('empfileForm'));
    ajax_load_data_from_file("/dekanat/employee/load_file/", formData)
}
