# coding: utf-8

"""
    Рисование различных графиков
"""

import numpy
from matplotlib import pyplot as plot


# цвета, используемые при рисовании
COLORS = ["#FF0000", "#00FF00", "#0000FF", "#AAAA00", "#AA00AA", "#00AAAA"]
COLORNUM = len(COLORS)

def plot_stacked_area_chart(x_values, y_series, legend):
    """ Рисует "диаграмму с областями и накоплением" (stacked area chart)
        x_values: точки по оси x
        y_series: список наборов точек по y
        legend: список подписей к наборам из y_series
    """
    # основано на http://stackoverflow.com/questions/2225995/how-can-i-create-stacked-line-graph-with-matplotlib
    y_data = numpy.row_stack(y_series)
    y_data_stacked = numpy.cumsum(y_data, axis=0)
    
    fig = plot.figure()
    ax1 = fig.add_subplot(111)
    ax1.legend(legend, 'upper center', shadow=True)
    for i in xrange(len(y_series)):
        low = y_data_stacked[i-1,:] if i >= 0 else 0
        high = y_data_stacked[i,:]
        #ax1.fill_between(x_values, low, high, facecolor=COLORS[i % COLORNUM], alpha=0.7)
        ax1.plot(x_values, y_series[i], color=COLORS[i % COLORNUM])
    plot.show()
    # TODO: нарисовать легенду
    
def plot_snapshot_blame(repo, relative=False):
    """
        График изменения вклада участников в проект во времени.
        
        relative: если False (по умолчанию) - график строится в абсолютных
                  величинах (строках),
                  иначе - в процентах от объема проекта
        
        commit.snapshot_blame должен уже быть вычислен для всех коммитов.
    """
    known_authors = set()
    # сначала определяем множество авторов
    for sha1 in repo.commit_order:
        commit = repo.commits[sha1]
        known_authors.update(commit.snapshot_blame.keys())
        
    known_authors = list(known_authors)
    known_authors.sort()
    
    f = open('b:/tr.txt','w')
    
    x_values = []
    y_values = [ list() for author in known_authors ]
    for ci, sha1 in enumerate(repo.commit_order[::-1]):
        commit = repo.commits[sha1]
        x_values.append(ci)
        total = 0.0
        for i, author in enumerate(known_authors):
            contrib = commit.snapshot_blame[author]
            y_values[i].append(contrib)
            total += contrib
        if relative and total > 0:
            for i, author in enumerate(known_authors):
                y_values[i][-1] = y_values[i][-1] / total * 100.0
        
        print >>f, sha1
        print >>f, commit.message
        for i, author in enumerate(known_authors):
            print >>f, y_values[i][-1], author
        print >>f, ""
    f.close()
    
    return plot_stacked_area_chart(x_values, y_values, known_authors)
    
        