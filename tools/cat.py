"""The cat tool: read a text file and return its contents."""

from tools.path_safety import is_path_safe


def cat(path):
    r'''Return the contents of a text file, or an error message.

    >>> import os, tempfile
    >>> with tempfile.TemporaryDirectory() as folder:
    ...     old = os.getcwd()
    ...     os.chdir(folder)
    ...     try:
    ...         with open('notes.txt', 'w', encoding='utf-8') as f:
    ...             _ = f.write('hello\nworld\n')
    ...         with open('binary.bin', 'wb') as f:
    ...             _ = f.write(b'\xff\xfe\x00\x80')
    ...         print(repr(cat('notes.txt')))
    ...         print(cat('missing.txt'))
    ...         print(cat('binary.bin'))
    ...         print(cat('.'))
    ...     finally:
    ...         os.chdir(old)
    'hello\nworld\n'
    Error: file not found
    Error: not a text file
    Error: could not read file

    Unsafe paths are rejected:

    >>> cat('/etc/passwd')
    'Error: path not allowed'
    >>> cat('../secret.txt')
    'Error: path not allowed'
    '''
    if not is_path_safe(path):
        return 'Error: path not allowed'
    try:
        with open(path, encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return 'Error: file not found'
    except UnicodeDecodeError:
        return 'Error: not a text file'
    except OSError:
        return 'Error: could not read file'
