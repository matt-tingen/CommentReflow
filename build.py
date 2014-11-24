from zipfile import ZipFile
import os
import pytest
import sys

SRC_DIR = 'src'
EXCLUDE = ['__pycache__', '__init__.py']
PACKAGE_FILENAME = 'CommentReflow.sublime-package'

test_result = pytest.main()

if test_result == 0:
    with ZipFile(PACKAGE_FILENAME, 'w') as sublime_package:
        for filename in os.listdir(SRC_DIR):
            if filename not in EXCLUDE:
                zip_name = os.path.join(SRC_DIR, filename)
                sublime_package.write(zip_name, filename)

    print('\nPackage created: ' + PACKAGE_FILENAME)
else:
    print('\nTests failed. Build aborted.')

sys.exit(test_result)