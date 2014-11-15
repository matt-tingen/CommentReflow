from zipfile import ZipFile
import os

SRC_DIR = 'src'

with ZipFile('CommentReflow.sublime-package', 'w') as sublime_package:
    for filename in os.listdir(SRC_DIR):
        zip_name = os.path.join(SRC_DIR, filename)
        sublime_package.write(zip_name, filename)
