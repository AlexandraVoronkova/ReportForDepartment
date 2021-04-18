let $tree = $('#tree');

$tree.treeview({
    data: getTree(),
    backColor: '#d6e2e2',
    expandIcon: 'glyphicon glyphicon-chevron-down',
    collapseIcon: 'glyphicon glyphicon-chevron-up',
    selectedBackColor: '#335d73',
    onhoverColor: '#99bdb9'
});

$tree.on('nodeSelected', function (event, node) {
    $.ajax({
        url: node.dbID + '/' + node.type + '/',
        dataType: "html",
        success: function (data, textStatus) {
            $('#contingent_table_body').html(data);
        },
        error: function () {
            dekanat_modals.alertError('При загрузке произошла ошибка');
        }
    })
});

$('#view_type_switch input').click(function () {
    window.location.href = window.location.pathname + '?viewtype=' + $(this).val()
});

