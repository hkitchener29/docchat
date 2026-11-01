"""Shared helper that keeps file tools inside the starting folder."""


def is_path_safe(path):
    """Return True if the path is relative and has no .. component.

    >>> is_path_safe('notes.txt')
    True
    >>> is_path_safe('docs/readme.md')
    True
    >>> is_path_safe('/etc/passwd')
    False
    >>> is_path_safe('../secret.txt')
    False
    >>> is_path_safe('docs/../../secret.txt')
    False
    """
    if path.startswith('/'):
        return False
    return '..' not in path.replace('\\', '/').split('/')
