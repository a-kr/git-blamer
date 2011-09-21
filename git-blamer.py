# coding: utf-8
u"""
    Git-blamer: основной модуль.
    
    Извлекает данные об истории репозитория и сохраняет их в виде статического
    веб-сайта.
    
    Использование: 
    git-blamer.py <путь к репозиторию> <путь к сайту>
"""
import os
import sys
import shutil

from repo import Repo
import cmds
import plot
import commitgraph
import dirtree

THIS_DIR = os.path.dirname(__file__)

def help():
    print __doc__
    exit()

def copy_common_files(target_dir):
    """ Копирует JS-библиотеки и графику в целевой каталог """
    files = [
        'commits-map.js',
        'dirtree.js',
        'jquery.js',
        'index.html',
        'img'
    ]
    for file in files:
        full_src = os.path.join(THIS_DIR, file)
        full_dst = os.path.join(target_dir, file)
        if os.path.isfile(full_src):
            shutil.copy(full_src, full_dst)
        elif os.path.isdir(full_src):
            if os.path.isdir(full_dst):
                shutil.rmtree(full_dst)
            shutil.copytree(full_src, full_dst)

def create_site(repo_path, target_dir):
    """ Записывает извлекаемые из репозитория данные в виде статического
        HTML-сайта в каталог target_dir """
            
    r = Repo.open(repo_path)
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
    
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    copy_common_files(target_dir)
        
    longest_path = r.get_longest_path()
    print "Found longest_path, len = ", len(longest_path)
    png, commit_coords = commitgraph.commit_network(r, set(longest_path))
    f = open(os.path.join(target_dir, 'graph.png'), 'wb')
    f.write(png)
    f.close()
    print "Plotting blame..."
    png = plot.plot_snapshot_blame(r, longest_path, commit_coords, relative=False)
    f = open(os.path.join(target_dir, 'blame-abs.png'), 'wb')
    f.write(png)
    f.close()
    print "Plotting blame (relative)..."
    png = plot.plot_snapshot_blame(r, longest_path, commit_coords, relative=True)
    f = open(os.path.join(target_dir, 'blame-rel.png'), 'wb')
    f.write(png)
    f.close()
    print "Done"

    print "Writing commit information..."
    f = open(os.path.join(target_dir, 'commits-data.js'), 'w')
    r.dump_commit_info_js(f, commit_coords)
    f.close()
    print "Done"

    root = dirtree.Directory.from_revision_blames(r.commits[r.head].snapshot_file_blames)

    print "Writing dirtree information..."
    f = open(os.path.join(target_dir, 'dirtree-data.js'), 'w')
    root.dump_to_js(f)
    f.close()
    print "Done"
    
def main():
    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        sys.argv = [sys.argv[0], 
                    r"c:\Dropbox\MSTU\8_Semester\dialog\question_thing",
                    r"b:\result"
                   ]
                   
    if len(sys.argv) != 3:
        help()
    repo_path = sys.argv[1]
    site_path = sys.argv[2]
    create_site(repo_path, site_path)
    
if __name__ == '__main__':
    main()