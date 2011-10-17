/*
    js.portal
    ~~~~~~~~~

    JavaScript for the portal.

    :copyright: (c) 2007-2011 by the Inyoka Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
*/
var added
$(function () { 
    (function () {
        $('a[name="dv-add"]').click(function (event) {
            event.preventDefault();
            var $row = $('<tr name="dv-new">' +
                '<td><input type="text" name="dv-name"/></td>' +
                '<td><input type="text" name="dv-number"/></td>' +
                '<td><input type="checkbox" name="dv-lts"/></td>' +
                '<td><input type="checkbox" name="dv-active"/></td>' +
                '<td><input type="checkbox" name="dv-current"/></td>' +
                '<td><input type="checkbox" name="dv-dev"/></td>' +
                '<td></td>' +
                '</tr>');
            var $td_del = $('<td></td>');
            var $a_del = $('<a href="#dv" name="dv-delete-new">Löschen</a>');
            $a_del.click(function (event) {
                event.preventDefault();
                $(this).parent().parent().remove();
            });
            $a_del.appendTo($td_del);
            $td_del.appendTo($row);
            $row.appendTo('#dv > tbody');
        });
        $('a[id|="dv-edit"]').click(function (event) {
            event.preventDefault();
            var $row = $(this).parent().parent();
            var version = $row.attr('id').substring(3); //strip the dv- from the version
            $row.children('[name|=dv]').each(function () {
                // iterate over all <td> elements.
                var key = $(this).attr('name').substr(3);
                var key = key.substr(0, key.length - 6);
                if (key == 'number' || key == 'name') {
                    var $e = $('<input type="text" name="dv-' + key + '"/>');
                    $e.val($(this).text());
                    $(this).removeAttr('name').empty();
                    $e.appendTo(this);
                } else if (key == 'lts' || key == 'active' || key == 'current' || key == 'dev') {
                    var $e = $('<input type="checkbox" name="dv-' + key + '" value="true"/>');
                    if ($(this).hasClass('dv-yes')) {
                        $e.attr('checked', 'checked');
                        //$e.val('on');
                    }
                    $(this).removeAttr('name').empty();
                    $e.appendTo(this);
                }
            });
            $(this).remove();
        });
        $('a[id|="dv-delete"]').click(function (event) {
            event.preventDefault();
            $(this).parent().parent().remove();
        });
        $('input[type="submit"]').click(function (event) {
            var distri_versions = new Array();
            var keys = ['number', 'name', 'lts', 'active', 'current', 'dev'];
            var number, name, lts, active, current, dev;
            $('tr[id|="dv"],tr[name="dev-new"]').each(function () {
                var values = Array();
                for (i = 0; i < keys.length; i++) {
                    var k = keys[i];
                    var $e = $(this).find('[name|=dv-' + k +']');
                    var val;
                    if ($e.is('INPUT')) {
                        if ($e.attr('type') == 'checkbox') {
                            val = ($e.is(':checked')) ? 'true' : 'false';
                        } else {
                            val = $e.val();
                        }
                    } else {
                        val = $e.text();
                    }
                    values.push('"' + k + '":"' + val + '"');
                }
                distri_versions.push('{' + values.join(',') + '}');
            });
            $('#id_distri_versions').val('[' + distri_versions.toString() + ']');
        });
    })();
});
