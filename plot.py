# coding: utf-8

"""
    Рисование различных графиков
"""
from cStringIO import StringIO

import Image, ImageDraw, ImageFont

# цвета, используемые при рисовании
COLORS = ["#FF0000", "#00FF00", "#0000FF", "#AAAA00", "#AA00AA", "#00AAAA"]
COLORNUM = len(COLORS)

    
def pil_stacked_area_chart(x_values, y_series, legend, stacked=True):
    """ Рисует "диаграмму с областями и накоплением" (stacked area chart)
        с помощью PIL (Python Image Library)
        x_values: точки по оси x
        y_series: список наборов точек по y
        legend: список подписей к наборам из y_series
        
        Если stacked=False, рисует обычный график с несколькими сериями значений.
        
        Возвращает байтовую строку с PNG-картинкой.
    """
    HEIGHT = 150
    MARGIN = 16
    LEGENDFIELD = 200 
    WIDTH = max(x_values)
    img = Image.new("RGB", (WIDTH + LEGENDFIELD, HEIGHT + MARGIN), "white")
    draw = ImageDraw.Draw(img)
    
    if stacked:
        # получаем новые серии: сумма серий 1..N, сумма серий 1..N-1, 1..N-2...
        # где N - число исходных серий
        new_series = []
        N = len(y_series)
        for i in xrange(N):
            new_points = [sum(y_series[si][j] for si in xrange(0, N-i)) 
                         for j in xrange(0, len(x_values))]
            new_series.append(new_points)
        y_series = new_series
    
    max_y = 0
    for points in y_series:
        max_y = max(max_y, max(points))
    max_y = float(max_y)
    
    def scale_y(y):
        return MARGIN + HEIGHT - y * HEIGHT / max_y
    
    for si, y_points in enumerate(y_series):
        points = [(0,HEIGHT+MARGIN)] + [(x_values[i], scale_y(y)) for i, y in enumerate(y_points)] + [(WIDTH,HEIGHT+MARGIN)]
        if stacked:
            # закрашиваем области
            draw.polygon(points, fill=COLORS[si % COLORNUM])
        else:
            draw.polygon(points, outline=COLORS[si % COLORNUM])
        
    # дорисовываем легенду
    font = ImageFont.truetype('tahoma.ttf', 10) #load_default()
    txt_w, txt_h = draw.textsize('Wfj', font=font)
    
    draw.text((WIDTH + 2, MARGIN + 2), str(int(max_y)), fill="black", font=font)
    for i, author in enumerate(legend[::-1]):
        y = MARGIN + 2 + txt_h * 2 + (txt_h + 2) * i
        draw.text((WIDTH + 4, y), author, fill=COLORS[i % COLORNUM], font=font)
    
        
    del draw
    
    f = StringIO()
    img.save(f, "PNG")
    return f.getvalue()
    
def plot_snapshot_blame(repo, path_to_plot, commit_coords, relative=False):
    """
        График изменения вклада участников в проект во времени.
        
        repo: объект Repo
        path_to_plot: список коммитов (обычно самый длинный путь в репозитории)
        commit_coords: словарь sha1 -> (x,y) согласно нарисованному графу коммитов
        
        relative: если False (по умолчанию) - график строится в абсолютных
                  величинах (строках),
                  иначе - в процентах от объема проекта
        
        commit.snapshot_blame должен уже быть вычислен для всех коммитов.
    """
    known_authors = set()
    # сначала определяем множество авторов
    for sha1 in path_to_plot:
        commit = repo.commits[sha1]
        known_authors.update(commit.snapshot_blame.keys())
        
    known_authors = list(known_authors)
    known_authors.sort()
    
    
    x_values = []
    y_values = [ list() for author in known_authors ]
    for ci, sha1 in enumerate(path_to_plot[::-1]):
        commit = repo.commits[sha1]
        x_values.append(commit_coords[sha1][0])
        total = 0.0
        for i, author in enumerate(known_authors):
            contrib = commit.snapshot_blame[author]
            y_values[i].append(contrib)
            total += contrib
        if relative and total > 0:
            for i, author in enumerate(known_authors):
                y_values[i][-1] = y_values[i][-1] / total * 100.0
        
        #print >>f, sha1
        #print >>f, commit.message
        #for i, author in enumerate(known_authors):
        #    print >>f, y_values[i][-1], author
        #print >>f, ""
    
    return pil_stacked_area_chart(x_values, y_values, known_authors)
    
        