import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY") or "offline-test")

def llm(messages, temperature=1):
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        temperature=temperature,
    )
    return completion.choices[0].message.content
class Chat:
    def __init__(self, system="You are a helpful assistant."):
        self.messages = [{"role": "system", "content": system}]

    def send_message(self, message, temperature=0.8):
        """Send a message and retain the reply.

        >>> from unittest.mock import patch
        >>> with patch.object(client.chat.completions, 'create') as request:
        ...     request.return_value.choices[0].message.content = 'Hello!'
        ...     chat = Chat(system='Be brief.')
        ...     first = chat.send_message('Hi', temperature=0)
        ...     second = chat.send_message('How are you?', temperature=0)
        >>> first, second
        ('Hello!', 'Hello!')
        >>> expected = [
        ...     {'role': 'system', 'content': 'Be brief.'},
        ...     {'role': 'user', 'content': 'Hi'},
        ...     {'role': 'assistant', 'content': 'Hello!'},
        ...     {'role': 'user', 'content': 'How are you?'},
        ...     {'role': 'assistant', 'content': 'Hello!'},
        ... ]
        >>> chat.messages == expected
        True
        >>> [c.kwargs['temperature'] for c in request.call_args_list]
        [0, 0]
        """
        self.messages.append({'role': 'user', 'content': message})
        reply = llm(self.messages, temperature=temperature)
        self.messages.append({'role': 'assistant', 'content': reply})
        return reply 

def repl(temperature=0.8):
    """Run the chatbot conversation.

    Test two inputs and capture the API requests:

    >>> from unittest.mock import patch, call
    >>> with patch('builtins.input', side_effect=['Hi', 'How are you?', EOFError]), patch.object(client.chat.completions, 'create') as request, patch('builtins.print') as output:
    ...     captured = []
    ...     replies = iter(['Hello!', 'Goodbye!'])
    ...     def respond(**kwargs):
    ...         captured.append([message.copy() for message in kwargs['messages']])
    ...         request.return_value.choices[0].message.content = next(replies)
    ...         return request.return_value
    ...     request.side_effect = respond
    ...     repl(temperature=0)
    >>> output.call_args_list
    [call('Hello!'), call('Goodbye!'), call()]
    >>> expected = [
    ...     {'role': 'system', 'content': 'You are a helpful assistant.You always speak like a pirate.'},
    ...     {'role': 'user', 'content': 'Hi'},
    ...     {'role': 'assistant', 'content': 'Hello!'},
    ...     {'role': 'user', 'content': 'How are you?'},
    ... ]
    >>> captured[1] == expected
    True
    >>> [c.kwargs['temperature'] for c in request.call_args_list]
    [0, 0]

    Test clean exit on EOFError:

    >>> with patch('builtins.input', side_effect=EOFError), patch.object(client.chat.completions, 'create'), patch('builtins.print') as output:
    ...     repl(temperature=0)
    >>> output.call_args_list
    [call()]

    Test clean exit on KeyboardInterrupt:

    >>> with patch('builtins.input', side_effect=KeyboardInterrupt), patch.object(client.chat.completions, 'create'), patch('builtins.print') as output:
    ...     repl(temperature=0)
    >>> output.call_args_list
    [call()]
    """
    chat = Chat(system="You are a helpful assistant.You always speak like a pirate.")
    try:
        while True:
            user_input = input("chat> ")
            print(chat.send_message(user_input, temperature=temperature))
    except (KeyboardInterrupt, EOFError):
        print()

if __name__ == "__main__":
    repl()
