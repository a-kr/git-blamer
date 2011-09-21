# coding: utf-8
import os
import sys
import shutil

from repo import Repo
import cmds
import plot
import commitgraph
import dirtree

THIS_DIR = os.path.dirname(__file__)

def copy_common_files(target_dir):
    """ Копирование JS-библиотек и графики в целевой каталог """
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

def main():
    repo_path = r"c:\Dropbox\MSTU\8_Semester\dialog\question_thing"
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
    
    target_dir = 'b:/result'
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

    import json

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
    
    
if __name__ == '__main__':
    main()