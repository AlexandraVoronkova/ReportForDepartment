let html_templates = {
    field_name: '<input name="field_name">',
    field_header: '<input class="form-control input-sm" name="field_header">',
    field_width: '<input class="form-control input-sm" type="number" name="field_width">',
    field_remove: '<button class="btn btn-sm btn-default delete-btn" onclick="delete_field_click(this)">' +
    '<span class="glyphicon glyphicon-trash"></span></button>'

};

function create_row(field_settings) {
    let row = $('<tr>');
    let td = $('<td style="display:none;"></td>').append($(html_templates.field_name).val(field_settings.name));
    row.append(td);
    td = $('<td>' + field_settings.label + '</td>');
    row.append(td);
    let header = field_settings.header;
    if (!header)
        header = field_settings.label;
    td = $('<td></td>').append($(html_templates.field_header).val(header));
    row.append(td);
    td = $('<td></td>').append($(html_templates.field_width));
    row.append(td);
    td = $('<td></td>').append($(html_templates.field_remove));
    row.append(td);
    let table = $('#fields_table');
    table.find('tbody').append(row);
    table.find('input[name="field_width"]').val(100 / (table.find('tr').length - 1));
    return row;
}

function add_field_click() {
    let field_name = $('#add_field_select').val();
    let all_fields = JSON.parse(document.getElementById('all_fields').textContent);
    let settings = all_fields.find(function (element, index, array) {
        return field_name === element.name;
    });
    let row = create_row(settings);
}


function delete_field_click(button) {
    let row = $(button).closest('tr');
    row.remove();
    let table = $('#fields_table');
    table.find('input[name="field_width"]').val(100 / (table.find('tr').length - 1));
}

function create_report() {
    let table = $('#fields_table tbody');
    let names = table.find('input[name="field_name"]').map(function () {
        return this.value
    }).get();
    let headers = table.find('input[name="field_header"]').map(function () {
        return this.value
    }).get();
    let widthes = table.find('input[name="field_width"]').map(function () {
        return this.value
    }).get();
    let fields = [];
    for (let i = 0; i < names.length; i++) {
        fields.push({name: names[i], header: headers[i], width: widthes[i]})
    }

    let params = {
        fields: fields,
        title: $('#report_title_input').val(),
        footer: $('#report_footer_input').val(),
        starosta: $('#report_starosta_checkbox').is(":checked"),
        kurator: $('#report_kurator_checkbox').is(":checked"),
        print_date: $('#report_print_date_checkbox').is(":checked"),
        print_number: $('#report_print_number_checkbox').is(":checked"),
        print_sign: $('#report_print_sign_checkbox').is(":checked"),
        is_portrait: $('#orientation').val() === 'portrait',
        brims: {
            top: $('#brim_top_input').val(),
            bottom: $('#brim_bottom_input').val(),
            left: $('#brim_left_input').val(),
            right: $('#brim_right_input').val(),
        }
    };
    let url = get_current_url() + 'print_custom_report/?params=' + JSON.stringify(params);
    if ($table.selected_all)
        url = url + '&filter=' + JSON.stringify(get_filter_data());
    else {
        url = url + '&students=' + $table.get_selected(0).join('&students=');
    }
    window.open(url);
}