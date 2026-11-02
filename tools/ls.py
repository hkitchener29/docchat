"""The ls tool: list files in a folder, like the shell's ls."""
import glob
import os

from tools.path_safety import is_path_safe


def ls(path='.'):
    r'''List the files in a folder, sorted alphabetically, one per line.

    >>> import tempfile
    >>> with tempfile.TemporaryDirectory() as folder:
    ...     for name in ['b.txt', 'a.txt', 'c.md']:
    ...         open(os.path.join(folder, name), 'w').close()
    ...     old = os.getcwd()
    ...     os.chdir(folder)
    ...     try:
    ...         print(ls())
    ...         print(ls('.'))
    ...     finally:
    ...         os.chdir(old)
    a.txt
    b.txt
    c.md
    a.txt
    b.txt
    c.md

    A subfolder can be listed too:

    >>> with tempfile.TemporaryDirectory() as folder:
    ...     os.mkdir(os.path.join(folder, 'sub'))
    ...     open(os.path.join(folder, 'sub', 'z.txt'), 'w').close()
    ...     old = os.getcwd()
    ...     os.chdir(folder)
    ...     try:
    ...         print(ls('sub'))
    ...     finally:
    ...         os.chdir(old)
    z.txt

    Unsafe paths are rejected:

    >>> ls('/etc')
    'Error: path not allowed'
    >>> ls('../')
    'Error: path not allowed'

    A missing folder gives an error message:

    >>> ls('no_such_folder')
    'Error: no such folder'
    '''
    if not is_path_safe(path):
        return 'Error: path not allowed'
    if not os.path.isdir(path):
        return 'Error: no such folder'
    names = glob.glob(os.path.join(path, '*'))
    return '\n'.join(sorted(os.path.basename(n) for n in names))
