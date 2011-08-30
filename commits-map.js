/* 
    База данных коммитов с пространственным индексом:
    коммиты ищутся по координатам (x,y) на графе коммитов, нарисованном Graphviz.
*/

var PROXIMITY_RADIUS = 5; /* радиус, в пределах которого ищутся "ближайшие" объекты */

var Commits = {
    /* теоретически здесь стоит сделать R-tree, но пока отложим этот момент. 
     * Мы знаем, что граф коммитов вытянут по ширине (x) и сравнительно невелик 
     * по игреку, поэтому нужно оптимизировать прежде всего поиск по x. */
    
    points: [], /* массив объектов {x, y, commit_info}, упорядоченный по x */   
    
    /* добавляет в базу коммит, расположенный на нарисованном графе в (x,y) */
    add: function (x, y, commit_info) {
        var newobj = {x: x, y: y, commit_info: commit_info};
        /* вставка в упорядоченный массив */
        var i = 0; 
        while (i < Commits.points.length && Commits.points[i].x < x) {
            i++;
        }
        Commits.points.splice(i, 0, newobj);
    },
    
    /* возвращает commit_info коммита, ближайшего к (x,y), или null, если такого нет */
    find: function (x, y) {
        /* двоичный поиск x в points */
        var lo, hi, mid;
        lo = 0; hi = Commits.points.length-1;
        while (lo + 1 < hi) {
            mid = Math.floor((lo + hi) / 2);
            if (Commits.points[mid].x == x) {
                lo = mid; hi = mid;
            } else if (Commits.points[mid].x > x) {
                hi = mid;
            } else {
                lo = mid;
            }
        }
        
        /* раздвигаем окно lo <= i <= hi, чтобы найти точки в радиусе PROXIMITY_RADIUS */
        while (lo > 0 && Commits.points[lo].x >= x - PROXIMITY_RADIUS)
            lo--;
        while (hi < Commits.points.length-1 && Commits.points[hi].x <= x + PROXIMITY_RADIUS)
            hi++;
            
        /* среди точек в окне ищем точку, ближайшую к (x,y) */
        var nearest_i = null;
        var nearest_dist_sq = Math.pow(PROXIMITY_RADIUS + 1, 2);
        for (var i = lo; i <= hi; i++) {
            var xi = Commits.points[i].x;
            var yi = Commits.points[i].y;
            var dist_sq = (x-xi)*(x-xi) + (y-yi)*(y-yi);
            if (dist_sq < nearest_dist_sq) {
                nearest_i = i;
                nearest_dist_sq = nearest_dist_sq;
            }
        }
        
        if (nearest_i === null)
            return null;
        return Commits.points[nearest_i].commit_info;
    },
};