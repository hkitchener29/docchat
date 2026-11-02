"""The load_image tool: add a local PNG image to the conversation."""
import base64

from tools.path_safety import is_path_safe


def load_image(chat, path):
    r'''Append a relative PNG file to chat.messages as an image_url block.

    >>> import os, tempfile
    >>> from types import SimpleNamespace as NS
    >>> data = b'\x89PNG\r\n\x1a\nfake'
    >>> chat = NS(messages=[])
    >>> with tempfile.TemporaryDirectory() as folder:
    ...     old = os.getcwd()
    ...     os.chdir(folder)
    ...     try:
    ...         with open('pic.png', 'wb') as f:
    ...             _ = f.write(data)
    ...         with open('pic.txt', 'w') as f:
    ...             _ = f.write('hi')
    ...         os.mkdir('dir.png')
    ...         loaded = load_image(chat, 'pic.png')
    ...         missing = load_image(chat, 'nope.png')
    ...         wrong = load_image(chat, 'pic.txt')
    ...         folder_error = load_image(chat, 'dir.png')
    ...     finally:
    ...         os.chdir(old)
    >>> loaded, missing, wrong, folder_error
    ('Image loaded', 'Error: file not found', 'Error: not a PNG file', 'Error: could not read file')
    >>> url = 'data:image/png;base64,' + base64.b64encode(data).decode()
    >>> chat.messages == [{'role': 'user', 'content': [
    ...     {'type': 'image_url', 'image_url': {'url': url}}]}]
    True

    Unsafe paths are rejected and the history does not change:

    >>> other = NS(messages=[])
    >>> load_image(other, '/etc/pic.png')
    'Error: path not allowed'
    >>> load_image(other, '../pic.png')
    'Error: path not allowed'
    >>> other.messages
    []
    '''
    if not is_path_safe(path):
        return 'Error: path not allowed'
    if not path.lower().endswith('.png'):
        return 'Error: not a PNG file'
    try:
        with open(path, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        return 'Error: file not found'
    except OSError:
        return 'Error: could not read file'
    url = 'data:image/png;base64,' + base64.b64encode(data).decode()
    chat.messages.append({'role': 'user', 'content': [
        {'type': 'image_url', 'image_url': {'url': url}}]})
    return 'Image loaded'
