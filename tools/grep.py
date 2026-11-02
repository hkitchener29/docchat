"""The grep tool: search files for lines that match a regex."""
import glob
import re

from tools.path_safety import is_path_safe


def grep(regex, path):
    r'''Return every line in the files matching path that matches regex.

    >>> import os, tempfile
    >>> with tempfile.TemporaryDirectory() as folder:
    ...     old = os.getcwd()
    ...     os.chdir(folder)
    ...     try:
    ...         with open('a.txt', 'w', encoding='utf-8') as f:
    ...             _ = f.write('TODO: fix bug\nall good\n')
    ...         with open('b.txt', 'w', encoding='utf-8') as f:
    ...             _ = f.write('another TODO\nfine\n')
    ...         with open('c.bin', 'wb') as f:
    ...             _ = f.write(b'\xff\xfe\x00\x80')
    ...         print(grep('TODO', 'a.txt'))
    ...         print(grep('TODO', '*.txt'))
    ...         print(repr(grep('nothing', '*.txt')))
    ...         print(grep(r'^all', 'a.txt'))
    ...         print(repr(grep('TODO', 'c.bin')))
    ...         print(repr(grep('TODO', 'missing.txt')))
    ...     finally:
    ...         os.chdir(old)
    TODO: fix bug
    TODO: fix bug
    another TODO
    ''
    all good
    ''
    ''

    Unsafe paths are rejected:

    >>> grep('TODO', '/etc/passwd')
    'Error: path not allowed'
    >>> grep('TODO', '../*.txt')
    'Error: path not allowed'

    A bad regex gives an error message:

    >>> grep('(', 'a.txt')
    'Error: invalid regex'
    '''
    if not is_path_safe(path):
        return 'Error: path not allowed'
    try:
        pattern = re.compile(regex)
    except re.error:
        return 'Error: invalid regex'
    matches = []
    for filename in sorted(glob.glob(path)):
        try:
            with open(filename, encoding='utf-8') as f:
                for line in f:
                    if pattern.search(line):
                        matches.append(line.rstrip('\n'))
        except (OSError, UnicodeDecodeError):
            continue
    return '\n'.join(matches)
