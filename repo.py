# coding: utf-8
import os

import cmds
import plot
import cPickle as pickle

class Repo(object):
    """ git-репозиторий """
    
    @classmethod
    def open(_class, path):
        """ Возвращает объект Repo для git-репозитория по указанному пути, 
            загружая ранее сохраненные результаты вычислений
        """
        pickled_path = os.path.join(path, '.git', 'blamer.pickled')
        if os.path.isfile(pickled_path):
            try:
                repo = pickle.load(open(pickled_path))
                new_head = repo.get_head_sha1()
                if new_head != repo.head:
                    # репозиторий обновился с прошлого раза
                    repo.head = new_head
                    repo.read_commits()
            except pickle.UnpicklingError:
                repo = Repo(path)
        else:
            repo = Repo(path)
        return repo
            
            
    def save(self):
        """ Сохраняет результаты вычислений на диск для ускорения последующих
            обращений к этому же репозиторию
        """
        pickled_path = os.path.join(self.path, '.git', 'blamer.pickled')
        f = open(pickled_path, 'w')
        pickle.dump(self, f)
        f.close()
            
    
    def __init__(self, path):
        """ Использовать Repo.open вместо прямого вызова конструктора
            path: путь к репозиторию
        """
        self.path = path
        self.commits = {} # sha1 -> Commit
        
        # выясняем sha1 у коммита HEAD
        self.head = self.get_head_sha1()
        
        self.commit_order = [] # sha1 коммитов в порядке от самого свежего до самого старого
        
        # первый коммит пока неизвестен
        self.first_commit = None
        
        self.read_commits()
        
    def get_head_sha1(self):
        """ Reads HEAD's sha1 from file """
        head_ref = open(os.path.join(self.path, '.git', 'HEAD')).read().split(': ')[1]
        head_ref = head_ref.strip().replace('.', '') # убираем точку в конце
        head_ref = head_ref.replace('/', os.sep)
        
        head = open(os.path.join(self.path, '.git', head_ref)).read().replace('.', '').strip()
        return head
    
    def blame_stats(self, file_path, rev_sha1):
        """ Число строк, принадлежащих каждому автору, в конкретном файле
            и ревизии.
            Возвращает словарь {имя автора: число строк}
        """
        return cmds.blame_stats(self.path, file_path, rev_sha1)
    
    def read_commits(self):
        """ Считывает коммиты из git log, заполняя self.commits """
        self.commit_order = [] # новые коммиты могли появиться в середине
                               # после merge с момента предыдущего обращения
                               # к репозиторию
        for commit in cmds.read_commits(self.path):
            if commit.sha1 not in self.commits:
                self.commits[commit.sha1] = commit
                commit.repo = self
            self.commit_order.append(commit.sha1)
        self.first_commit = commit.sha1
        
    def ignore_file(self, file_path):
        """ Возвращает true, если файл с указанным именем не должен учитываться
            при подсчете метрик (например, является бинарным)
        """
        if 'aot_seman' in file_path:
            return True
        bad_extensions = (".pdf", ) # Git считает pdf текстовыми
        for ext in bad_extensions:
            if file_path.endswith(ext):
                return True
        return False
        
    def compute_blame(self):
        """ Вычисляет информацию об авторстве для всех файлов и коммитов
            в репозитории
        """
        # вычисление должно идти от более старых коммитов к более новым,
        # т.к. новые используют информацию об авторстве из старых
        for i, sha1 in enumerate(self.commit_order[::-1]):
            commit = self.commits[sha1]
            if commit.snapshot_blame is not None:
                continue # пропускаем коммиты, обработанные при прошлой загрузке
            # данные об авторстве файлов, измененных в этом коммите
            for file_path, _, __ in commit.changes:
                if self.ignore_file(file_path):
                    continue
                try:
                    blame = cmds.blame_stats(self.path, file_path, commit.sha1)
                except Exception as e:
                    if 'no such path' in unicode(e):
                        blame = None
                    else:
                        raise
                commit.blames[file_path] = blame
            
            # интеграция данных
            commit.compute_snapshot_blame()
            print "completed", i, "of", len(self.commit_order)

r = Repo.open(r"c:\Dropbox\MSTU\8_Semester\dialog\question_thing")
print "Repo loaded."
print "Blaming the authors..."
r.compute_blame()
print "Done."
print "Saving data..."
r.save()
print "Done."
print "Stats for the latest revision:"
print r.commits[r.head].snapshot_blame
print "Plotting..."

plot.plot_snapshot_blame(r, relative=True)
