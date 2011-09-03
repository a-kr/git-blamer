/* DirTree: файловый браузер */

var DirTree = {
    entries: [],
    
    /* добавление новой записи (вызывается из dirtree-data.js на стадии загрузки) */
    add: function (entry) {
        DirTree.entries.push(entry);
    },
    
    /* поиск записей, у которых entry.path = path */
    find_children: function (path) {
        var results = [];
        for (var i = 0; i < DirTree.entries.length; i++) {
            if (DirTree.entries[i].path == path)
                results.push(DirTree.entries[i]);
        }
        return results;
    },
    
    /* создание <TR> по записи */
    make_row: function (entry) {
        var blame_lines = [];
        for (var i = 0; i < entry.blame.length; i++) {
            var author = entry.blame[i][0];
            var impact = entry.blame[i][1];
            blame_lines.push(Math.round(impact) + "% " + author);
        }
        var blame = blame_lines.join(', ');
        
        var tr = $('<tr>').addClass('dirtree_row').data('entry', entry).data('expanded', false);
        $('<td>').appendTo(tr).addClass('dirtree_name').append(
            $('<div>').addClass('dt_' + entry.type).css('padding-left', 20).text(entry.name)
        ).css('padding-left', entry.depth * 16);
        $('<td>').appendTo(tr).addClass('dirtree_lines').text(entry.lines.toString());
        $('<td>').appendTo(tr).addClass('dirtree_blame').text(blame);
        
        tr.click(DirTree.on_row_click);
        return tr;
    },
    
    /* загрузка записей корневого каталога в таблицу браузера.
       table_id - #id таблицы, например "#filebrowser"
    */
    load_root: function (table_id) {
        var root_entries = DirTree.find_children('/');
        var table = $(table_id);
        for (var i = 0; i < root_entries.length; i++) {
            var tr = DirTree.make_row(root_entries[i]);
            table.append(tr);
        }
    },
    
    on_row_click: function (evt) {
        var row = $(evt.currentTarget);
        var path = row.data('entry').path + row.data('entry').name + '/';
        if (row.data('expanded') == false) {
            row.data('expanded', true);
            var entries = DirTree.find_children(path);
            for (var i = entries.length - 1; i >= 0; i--) {
                var tr = DirTree.make_row(entries[i]);
                tr.insertAfter(row);
            }
        } else {
            row.data('expanded', false);
            var child_rows = $('.dirtree_row').filter( function (i) {
                return $(this).data('entry').path == path;
            });
            child_rows.remove();
        }
    },
};