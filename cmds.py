# coding: utf-8
""" Интерфейс к командам git 

    Справка о параметрах функций:
    repo_path: везде --- полный путь к репозиторию (т.е. каталогу, имеющему
               подкаталог .git)
    file_path: везде --- путь к файлу относительно корня репозитория
    rev_sha1: везде --- хэш sha1 в текстовом виде (или его первые
               несколько байт)

"""

import os
import re
from subprocess import *

from objects import Commit, Blame

class GitError(Exception):
    pass
    
def author_alias(author_name):
    """ Подмена имени автора (в случае, если у автора несколько имен) """
    # TODO git log --format='%aN <%aE>' | sort -u
    return author_name

def git_cmd_start(repo_path):   
    """ Формирует начало командной строки для обращения к командам git
        из произвольного каталога
    """
    return ['git', '--git-dir=' + os.path.join(repo_path, '.git'),
            '--work-tree=' + repo_path]
            
# запись об измененном файле в git log --numstat
r_numstat = re.compile('(\d+)\t(\d+)\t(.*)')

def read_commits(repo_path):
    """ Возвращает (yield) объекты Commit для всех коммитов """
    commit = None
    cmds = git_cmd_start(repo_path) + ['log', '-m', '--parents', '--numstat', '--date=iso'] 
    process = Popen(cmds, stdout=PIPE, stderr=PIPE)
    
    for line in iter(process.stdout):
        line = line.replace('\n', '')
        if line.startswith("Author: "):
            commit.author = author_alias(line[len("Author: "):])
        elif line.startswith("Date: "):
            commit.date = line[len("Date: "):]
            commit.date = commit.date[:-6].strip() # убираем +0300
        elif line.startswith("commit "):
            if commit: 
                yield commit
            if ' (from' in line:
                line = line[:line.index(' (from')]
            hashes = line.split(' ')[1:]
            commit = Commit(hashes[0], hashes[1:])
        elif line.startswith("    "):
            commit.message = line[4:]
        else:
            m = r_numstat.match(line) 
            if m:
                f_add, f_rem, f_name = m.groups()
                if f_add != '-': # не бинарный
                    f_add, f_rem = int(f_add), int(f_rem)
                    commit.changes.append((f_name, f_add, f_rem))
                
    if commit: 
        yield commit
        
    errors = process.stderr.read()
    if errors:
        raise GitError("log: " + errors)

def blame_stats(repo_path, file_path, rev_sha1):
    """ Выполняет git blame для указанного файла и ревизии.
        Подсчитывает число строк, принадлежащих каждому автору.
        
        Возвращает объект Blame
    """
    # '--' нужен, чтобы blame'ить удаленные файлы
    cmds = git_cmd_start(repo_path) + ['blame', '-p', '--encoding=utf-8', '--', file_path, rev_sha1] 
    process = Popen(cmds, stdout=PIPE, stderr=PIPE)
    
    #if errors:
    #    raise GitError("blame: " + errors)
    
    commit_authors = {} # словарь sha1 -> author
    blame = Blame() # по сути словарь: author -> число строк
    
    #out = out.decode('utf-8')
    
    # будем читать вывод по одной строчке
    line_feeder = iter(process.stdout)
    def next_line():
        try:
            return line_feeder.next()
        except StopIteration:
            return None
            
    while True:
        line = next_line()
        if line is None:
            break
        # начало заголовка: sha1 
        sha1 = line.split(' ')[0]
        if not sha1:
            break
            
        line = next_line()
        # остаток заголовка
        author = author_mail = ""
        while not line.startswith('\t'):    
            if line.startswith('author '):
                author = line.split(' ', 1)[1].strip()
            elif line.startswith('author-mail'):
                author_mail = line.split(' ', 1)[1].strip()
                
            line = next_line()
            if line is None:
                break
                
        if line is None:
            break # в файле больше нет строк данных
        if author:
            commit_authors[sha1] = author_alias(author + ' ' + author_mail)
        blame[commit_authors[sha1]] += 1
        
    errors = process.stderr.read()
    if errors:
        raise GitError("blame: " + errors)
        
    return blame