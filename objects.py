# coding: utf-8

from UserDict import IterableUserDict


class Blame(IterableUserDict):
    """ Информация об авторстве.
        Объект ведет себя как словарь: имя автора -> число строк, ему принадлежащих
    """
    def __init__(self, data=None):
        IterableUserDict.__init__(self)
        if data:
            self.data = data
    
    def __missing__(self, key):
        """ Значение по умолчанию для отсутствующих объектов """
        return 0
        
    def update_add(self, blame2):
        """ Добавляет значения из blame2 к данному объекту Blame """
        for name in blame2:
            self[name] += blame2[name]
            
    def size(self):
        """ Возвращает суммарное число строк, отраженных в этом Blame """
        return sum(self.values())
        
    def author_impacts(self, lower_limit=0.0):
        """ Сортирует авторов по убыванию вклада.
            lower_limit: минимальный вклад (в %) для попадания в список.
            Возвращает список кортежей (имя автора, доля в процентах 0.0 - 100.0)
        """
        authors = sorted(self.keys(), key=lambda auth: self[auth], reverse=True) 
        total = self.size()
        if total == 0:
            total = 1 # 0 / 1 все равно == 0%
        total = float(total)
        impacts = ((a, self[a] / total * 100.0) for a in authors)
        return [(a,i) for (a,i) in impacts if i >= lower_limit]
    def largest_author(self):
        """ Определяет автора с наибольшим вкладом.
            Возвращает кортеж (имя автора, доля в процентах 0.0 - 100.0)
        """
        authors = self.author_impacts()
        return authors[0]
        
    def __repr__(self):
        return u'Blame({\n' + u',\n'.join("\t" + repr(key) + u": " + repr(val)
            for key, val in self.data.iteritems()) + u"\n})"

class Commit(object):
    """ Описание коммита в репозитории """
    def __init__(self, sha1, parent_sha1s):
        """ sha1: хэш данного коммита
            parent_sha1s: список хэшей родительских коммитов
        """
        self.sha1 = sha1
        self.author = ""
        self.date = None
        self.message = ""
        self.parents = parent_sha1s
        
        self.repo = None # ссылка на объект Repo задается в его методе read_commits
        
        # информация о файлах, измененных в коммите:
        self.changes = [] # список кортежей
                          # (имя файла, строк добавлено, строк удалено)
        self.blames = {} # имя файла -> Blame для этого файла
        
        # данные об авторстве для текущего состояния дерева в целом
        self.snapshot_blame = None
        # ...для отдельных файлов текущего дерева
        # (словарь путь_к_файлу -> Blame)
        self.snapshot_file_blames = None
    
    def compute_snapshot_blame(self):
        """ Вычисление авторства для всех файлов текущего состояния дерева
            в отдельности и для дерева в целом.
            
            Состояние дерева вычисляется рекурсивно, складываясь из изменений
            в текущем коммите и состояния деревьев родительских коммитов.
        """
        # определение состояния родительских деревьев
        parent_blames = {}
        parent_commits = [self.repo.commits[sha1] for sha1 in self.parents]
        for parent_commit in parent_commits:
            blames = parent_commit.snapshot_file_blames
            assert blames is not None
            parent_blames.update(blames)
            
        # добавление данных о файлах, измененных в текущем коммите
        blames = dict(parent_blames)
        for filename in self.blames:
            blames[filename] = self.blames[filename]
            if blames[filename] is None:
                del blames[filename]
                
        # суммирование данных по всем файлам в текущем дереве
        self.snapshot_blame = Blame()
        for filename in blames:
            self.snapshot_blame.update_add(blames[filename])
        self.snapshot_file_blames = blames
        
        # дочерние коммиты будут обращаться к snapshot_file_blames

