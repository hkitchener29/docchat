"""The compact tool: replace a long conversation with a short summary."""

PROMPT = 'Summarize our conversation so far in at most five lines.'


def compact(chat):
    r'''Ask the model to summarize the chat, then keep only that summary.

    >>> from unittest.mock import patch
    >>> from types import SimpleNamespace as NS
    >>> chat = NS(messages=[
    ...     {'role': 'user', 'content': 'Hi'},
    ...     {'role': 'assistant', 'content': 'Hello'},
    ... ])
    >>> seen = []
    >>> def fake_llm(messages):
    ...     seen.append(list(messages))
    ...     return NS(content='one\ntwo\nthree\nfour\nfive\nsix\nseven')
    >>> with patch('chat.llm', fake_llm):
    ...     summary = compact(chat)
    >>> summary
    'one\ntwo\nthree\nfour\nfive'
    >>> chat.messages
    [{'role': 'system', 'content': 'one\ntwo\nthree\nfour\nfive'}]
    >>> [m['content'] for m in seen[0]][:2]
    ['Hi', 'Hello']
    >>> len(seen[0])
    3
    '''
    import chat as chat_module
    history = list(chat.messages) + [{'role': 'user', 'content': PROMPT}]
    reply = chat_module.llm(history)
    text = getattr(reply, 'content', reply) or ''
    summary = '\n'.join(text.strip().splitlines()[:5])
    chat.messages = [{'role': 'system', 'content': summary}]
    return summary
