# coding: utf-8

import os
import json
from collections import defaultdict

from objects import Blame

class Directory(object):
    def __init__(self):
        self.dirs = defaultdict(Directory)  # подкаталоги: имя -> объект Directory
        self.files = {} # файлы: имя -> объект Blame
        self.blame = None # объект Blame для каталога в целом
        
    @classmethod
    def from_revision_blames(self, blame_dict):
        """ Восстанавливает дерево каталогов по набору путей к файлам.
            blame_dict: словарь "путь" -> объект Blame.
            
            Возвращает объект Directory.
        """
        root = Directory()
        for path in blame_dict:
            root.addfile(path, blame_dict[path])
        root.compute_blame()
        return root
        
    def addfile(self, path, blame): 
        """ Добавление файла в дерево каталогов.
            path: путь относительно текущего каталога.
            blame: информация об авторстве для файла (объект Blame)
        """
        if isinstance(path, basestring):
            path = path.split('/')
        if len(path) == 1:
            self.files[path[0]] = blame
        else:
            dirname, rest_of_path = path[0], path[1:]
            self.dirs[dirname].addfile(rest_of_path, blame)
            
    def compute_blame(self):
        """ Вычисление авторства данного каталога на основании данных об 
            авторстве подкаталогов и файлов.
            Создает и возвращает экземпляр Blame, попутно сохраняя его в 
            поле self.blame.
        """
        self.blame = Blame()
        for subdir in self.dirs:
            dirblame = self.dirs[subdir].compute_blame()
            self.blame.update_add(dirblame)
        for filename in self.files:
            self.blame.update_add(self.files[filename])
        return self.blame
        
    def printf(self, depth=0):
        for subdir in self.dirs:
            print '   ' * depth, subdir + '/', ["%s %3.0f%%" % impact for impact in self.dirs[subdir].blame.author_impacts()]
            self.dirs[subdir].printf(depth+1)
        for file in self.files:
            print '   ' * depth, file, ["%s %3.0f%%" % impact for impact in self.files[file].author_impacts()]
            
    def dump_to_js(self, file, path='/', depth=0):
        """ Запись информации о содержимом каталога в файл JavaScript """
        def write(entry_type, entry_name, entry_blame):
            lines = entry_blame.size()
            blame = entry_blame.author_impacts(lower_limit=5.0)
            json_blame = json.dumps(blame)
            print >>file, """DirTree.add({
                type: "%s",
                depth: %s,
                path: "%s",
                name: "%s",
                lines: %d,
                blame: %s
})""" % (entry_type, depth, path, entry_name, lines, json_blame)
            
                
        for subdir in self.dirs:
            write('dir', subdir, self.dirs[subdir].blame)
            self.dirs[subdir].dump_to_js(file, path + subdir + '/', depth+1)
        for filename in self.files:
            write('file', filename, self.files[filename])
            
            
         