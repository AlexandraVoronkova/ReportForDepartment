var $tree = $('#tree');
var $table = $('#contingent_table').selecting_table({multiselect: true});

var dp = $('#historyDate').datepicker().data('datepicker');
if (getDate())
    dp.selectDate(new Date(getDate()));
else
    dp.selectDate(new Date());


$tree.treeview({
    data: getTree(),
    backColor: '#d6e2e2',
    expandIcon: 'glyphicon glyphicon-chevron-down',
    collapseIcon: 'glyphicon glyphicon-chevron-up',
    selectedBackColor: '#335d73',
    onhoverColor: '#99bdb9'
});


$tree.on('nodeSelected', function (event, node) {
    var status = $('#status_select').val();
    $.ajax({
        url: "group/" + node.dbID + '/' + node.type + '/',
        dataType: "html",
        success: function (data, textStatus) {
            $table.find('#groupTable').html(data);
        },
        error: function () {
            dekanat_modals.alertError('При загрузке произошла ошибка');
        }
    })
});

$('#status_select').on('change', function () {
    let status = $(this).val();
    let node = $tree.treeview('getSelected', 1)[0];
    if (!node)
        node = $tree.treeview('getNode', 0);

    if (status == 1)
        $('#print_dropdown_menu').show();
    else
        $('#print_dropdown_menu').hide();

    $.ajax({
        url: "group/" + node.dbID + '/' + node.type + '/' ,
        dataType: "html",
        success: function (data, textStatus) {
            $table.find('#groupTable').html(data);
        },
        error: function () {
            dekanat_modals.alertError('При загрузке произошла ошибка');
        }
    });
});

$('#history_btn').click(function (ev) {
    window.location.href = '/dekanat/contingent/group_date/' + $('#historyDate').val();
});

$('#view_type_switch input').click(function () {
    window.location.href = window.location.pathname + '?viewtype=' + $(this).val()
});

$('.education_type').click(function () {
    let filter_options = $(this).attr('edu-type');
    if ((filter_options == '1') || (filter_options == '2'))
    {
        window.location.href = window.location.pathname + '?education_type=' + filter_options
    }
    else{
        window.location.href = window.location.pathname
    }
});
