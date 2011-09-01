# coding: utf-8

"""
    Визуализация графа коммитов 
"""

from subprocess import *
from cStringIO import StringIO
import re

def commit_network(repo, commits_to_highlight=set()):
    """ Рисует граф коммитов с помощью Graphviz.
    
        commits_to_highlight: множество коммитов, рисуемых с черной (а не серой)
        закраской.
        
        Возвращает кортеж (png, commit_coords), где
          -- png - байты png-изображения;
          -- commit_coords - словарь sha1 -> (x,y) (координаты коммитов в png)
    """
    
    # этап первый: препроцессинг, на выходе получаем DOT-файл с координатами
    process = Popen(['dot', ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    
    dot = prepare_dot(repo, commits_to_highlight)
    
    out, errors = process.communicate(dot)
    if errors:
        raise Exception(errors)
    
    commit_coords = extract_commit_coords(out)
    assert len(commit_coords) == len(repo.commits)
    # если вдруг нужно, то в этом месте можно и подправить координаты в out
    
    # этап второй: получаем PNG
    process = Popen(['dot', '-Tpng'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    png, errors = process.communicate(out)
    if errors:
        raise Exception(errors)
    
    return png, commit_coords

def prepare_dot(repo, commits_to_highlight):
    """ Составление описания графа коммитов на языке DOT """
    dot = StringIO()
    
    print >>dot, """digraph G {
        node [shape=circle, width=0.05, height=0.05, style=filled, fillcolor=gray, color=black, label=""]
        edge [arrowhead=none]
        nodesep=0.15
        ranksep=0.15
        rankdir=LR
    """
    for commit in repo.commits.values():
        attrs = []
        if commit.sha1 in commits_to_highlight:
            attrs.append('fillcolor="black"')
        print >>dot, "N" + commit.sha1, "[" + ', '.join(attrs) + "]"
        for parent_sha1 in commit.parents:
            print >>dot, "N" + parent_sha1, "->", "N" + commit.sha1
    print >>dot, "}"
    
    return dot.getvalue()
    
# границы рисунка в DOT
re_boundary = re.compile(r'graph \[bb="0,0,(\d+),(\d+)"\];')
# поиск описания узлов-коммитов в DOT
re_nodes = re.compile(r'\s+N([a-f\d]+)\s+\[.*pos="(\d+),(\d+)".*')
    
# коэф. преобразования единиц DOT в пиксели
# (1 point, 1/72th of an inch --> 96 dpi)
DOT_SCALE = 96.0 / 72.0 
    
def extract_commit_coords(dot):
    """ Извлечение координат узлов-коммитов из DOT-файла, получаемого в результате
        препроцессинга
    """
    match = re_boundary.search(dot)
    if not match:
        import pdb; pdb.set_trace()
    width, height = match.groups()
    width, height = float(width) * DOT_SCALE, float(height) * DOT_SCALE
    
    commit_coords = {}
    for line in dot.split('\n'):
        match = re_nodes.match(line)
        if match:
            sha1, x, y = match.groups()
            x,y = int(x) * DOT_SCALE, int(y) * DOT_SCALE
            y = height - y # инвертируем ось Y
            x = x + 5 # смещения подобраны экспериментально, чтобы
            y = y + 5 # координаты соответствовали центрам нарисованных вершин
            commit_coords[sha1] = (int(x), int(y))
    return commit_coords
            
    