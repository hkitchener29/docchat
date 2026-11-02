"""The calculate tool: safely evaluate an arithmetic expression."""
import re

ALLOWED = re.compile(r'[0-9+\-*/(). %]+')


def calculate(expression):
    r'''Evaluate an arithmetic expression and return the result as a string.

    >>> calculate('2 + 3')
    '5'
    >>> calculate('(2 + 3) * 4')
    '20'
    >>> calculate('10 / 4')
    '2.5'
    >>> calculate('7 % 3')
    '1'
    >>> calculate('2 * (3 + 4) - 5')
    '9'

    Anything other than numbers, spaces, parentheses, and operators is rejected:

    >>> calculate('__import__("os").getcwd()')
    'Error: invalid expression'
    >>> calculate('abs(-3)')
    'Error: invalid expression'
    >>> calculate('open("notes.txt")')
    'Error: invalid expression'

    Expressions that are allowed characters but can't be computed give errors:

    >>> calculate('1 / 0')
    'Error: division by zero'
    >>> calculate('2 +')
    'Error: invalid expression'
    >>> calculate('')
    'Error: invalid expression'
    '''
    if not ALLOWED.fullmatch(expression):
        return 'Error: invalid expression'
    try:
        return str(eval(expression, {'__builtins__': {}}, {}))
    except ZeroDivisionError:
        return 'Error: division by zero'
    except Exception:
        return 'Error: invalid expression'
