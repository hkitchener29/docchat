"""A command-line chatbot that answers questions about files using tools."""
import json
import os
import shlex

from dotenv import load_dotenv
from groq import Groq

from tools.calculate import calculate
from tools.cat import cat
from tools.grep import grep
from tools.ls import ls
from tools.path_safety import is_path_safe  # noqa: F401

load_dotenv()

SYSTEM = "You are a helpful assistant. You always speak like a pirate."
MODEL = 'openai/gpt-oss-20b'  # change this to a model your key can use

FUNCTIONS = {'calculate': calculate, 'ls': ls, 'cat': cat, 'grep': grep}


def _schema(name, description, properties, required):
    """Build the tool description the model sees for one function."""
    return {
        'type': 'function',
        'function': {
            'name': name,
            'description': description,
            'parameters': {
                'type': 'object',
                'properties': {k: {'type': 'string', 'description': v}
                               for k, v in properties.items()},
                'required': required,
            },
        },
    }


TOOLS = [
    _schema('calculate', 'Evaluate an arithmetic expression.',
            {'expression': 'The expression, such as (2 + 3) * 4'},
            ['expression']),
    _schema('ls', 'List the files in a folder (default: current folder).',
            {'path': 'Relative folder path'}, []),
    _schema('cat', 'Return the contents of a text file.',
            {'path': 'Relative file path'}, ['path']),
    _schema('grep', 'Return lines of files (path may be a glob) that match a regex.',
            {'regex': 'The regular expression', 'path': 'Relative path or glob'},
            ['regex', 'path']),
]


def get_client():
    """Create a Groq client using the API key from the environment."""
    return Groq(api_key=os.environ['GROQ_API_KEY'])


def llm(messages, tools=None, temperature=0.8):
    """Send the conversation to the model and return its reply message."""
    client = get_client()  # created only when a request is made
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        temperature=temperature,
        timeout=30,
    )
    return response.choices[0].message


class Chat:
    """Hold a conversation history and let the model call file tools.

    Tool requests from the model run automatically, and slash commands run
    a tool directly. Either way the result is added to the history.

    >>> from unittest.mock import patch
    >>> with patch('chat.get_client') as get_client:
    ...     request = get_client.return_value.chat.completions.create
    ...     message = request.return_value.choices[0].message
    ...     message.content = 'Hello!'
    ...     message.tool_calls = None
    ...     chat = Chat(system='Be brief.')
    ...     first = chat.send_message('Hi', temperature=0)
    ...     second = chat.send_message('How are you?', temperature=0)
    >>> first, second
    ('Hello!', 'Hello!')
    >>> chat.messages == [
    ...     {'role': 'system', 'content': 'Be brief.'},
    ...     {'role': 'user', 'content': 'Hi'},
    ...     {'role': 'assistant', 'content': 'Hello!'},
    ...     {'role': 'user', 'content': 'How are you?'},
    ...     {'role': 'assistant', 'content': 'Hello!'},
    ... ]
    True
    >>> [c.kwargs['temperature'] for c in request.call_args_list]
    [0, 0]

    A tool request from the model runs the function and sends back the result:

    >>> from types import SimpleNamespace as NS
    >>> call = NS(id='call-1', function=NS(
    ...     name='calculate', arguments='{"expression": "2 + 3"}'))
    >>> asked = NS(content=None, tool_calls=[call], model_dump=lambda **kw: {
    ...     'role': 'assistant',
    ...     'tool_calls': [{'id': 'call-1', 'type': 'function', 'function': {
    ...         'name': 'calculate', 'arguments': '{"expression": "2 + 3"}'}}]})
    >>> answered = NS(content='It is 5.', tool_calls=None)
    >>> replies = iter([asked, answered])
    >>> seen = []
    >>> def fake_llm(messages, tools=None, temperature=0.8):
    ...     seen.append([m.copy() for m in messages])
    ...     return next(replies)
    >>> with patch('chat.llm', fake_llm):
    ...     chat = Chat(system='Be brief.')
    ...     answer = chat.send_message('What is 2 + 3?')
    >>> answer
    'It is 5.'
    >>> seen[1][-1]
    {'role': 'tool', 'tool_call_id': 'call-1', 'content': '5'}
    >>> chat.messages[-1]
    {'role': 'assistant', 'content': 'It is 5.'}

    A slash command runs a tool directly and puts the output in the history:

    >>> chat = Chat(system='Be brief.')
    >>> chat.run_slash('/calculate 2 + 3')
    '5'
    >>> chat.messages[-1]['role']
    'user'
    >>> '/calculate 2 + 3' in chat.messages[-1]['content']
    True
    >>> chat.messages[-1]['content'].endswith('5')
    True
    >>> chat.run_slash('/nothing')
    'Error: unknown command nothing'
    >>> chat.run_slash('/grep onlyone')
    'Error: wrong arguments for grep'
    >>> chat.run_slash('/')
    'Error: no command given'
    """

    def __init__(self, system=SYSTEM):
        self.messages = [{"role": "system", "content": system}]

    def run_tool(self, name, arguments):
        """Run the named tool with a dictionary of arguments and return its result."""
        if name not in FUNCTIONS:
            return f'Error: unknown tool {name}'
        try:
            return str(FUNCTIONS[name](**arguments))
        except TypeError:
            return f'Error: wrong arguments for {name}'

    def run_slash(self, line):
        """Run a /command line directly and add its output to the history."""
        try:
            parts = shlex.split(line[1:])
        except ValueError:
            return 'Error: could not parse command'
        if not parts:
            return 'Error: no command given'
        name, args = parts[0], parts[1:]
        if name not in FUNCTIONS:
            return f'Error: unknown command {name}'
        if name == 'calculate':
            args = [' '.join(args)]
        try:
            output = str(FUNCTIONS[name](*args))
        except TypeError:
            return f'Error: wrong arguments for {name}'
        self.messages.append({'role': 'user',
                              'content': f'{line}\n{output}'})
        return output

    def send_message(self, message, temperature=0.8):
        """Send a message, run any tools the model requests, and return its answer."""
        self.messages.append({'role': 'user', 'content': message})
        for _ in range(10):
            reply = llm(self.messages, tools=TOOLS, temperature=temperature)
            if not reply.tool_calls:
                break
            self.messages.append(reply.model_dump(exclude_none=True))
            for call in reply.tool_calls:
                try:
                    arguments = json.loads(call.function.arguments or '{}')
                except json.JSONDecodeError:
                    arguments = None
                if isinstance(arguments, dict):
                    result = self.run_tool(call.function.name, arguments)
                else:
                    result = 'Error: could not read tool arguments'
                self.messages.append({'role': 'tool',
                                      'tool_call_id': call.id,
                                      'content': result})
        content = reply.content or ''
        self.messages.append({'role': 'assistant', 'content': content})
        return content


def repl(temperature=0.8):
    """Run the chatbot conversation, handling /commands without the model.

    >>> from unittest.mock import patch, call
    >>> with patch('builtins.input', side_effect=['Hi', 'How are you?', EOFError]), patch('chat.get_client') as get_client, patch('builtins.print') as output:
    ...     request = get_client.return_value.chat.completions.create
    ...     captured = []
    ...     replies = iter(['Hello!', 'Goodbye!'])
    ...     def respond(**kwargs):
    ...         captured.append([m.copy() for m in kwargs['messages']])
    ...         message = request.return_value.choices[0].message
    ...         message.content = next(replies)
    ...         message.tool_calls = None
    ...         return request.return_value
    ...     request.side_effect = respond
    ...     repl(temperature=0)
    >>> output.call_args_list
    [call('Hello!'), call('Goodbye!'), call()]
    >>> captured[1] == [
    ...     {'role': 'system', 'content': SYSTEM},
    ...     {'role': 'user', 'content': 'Hi'},
    ...     {'role': 'assistant', 'content': 'Hello!'},
    ...     {'role': 'user', 'content': 'How are you?'},
    ... ]
    True

    A slash command prints its output and makes no model request:

    >>> with patch('builtins.input', side_effect=['/calculate 2 + 3', EOFError]), patch('chat.get_client') as get_client, patch('builtins.print') as output:
    ...     repl(temperature=0)
    >>> output.call_args_list
    [call('5'), call()]
    >>> get_client.called
    False

    Test clean exit on EOFError:

    >>> with patch('builtins.input', side_effect=EOFError), patch('builtins.print') as output:
    ...     repl(temperature=0)
    >>> output.call_args_list
    [call()]

    Test clean exit on KeyboardInterrupt:

    >>> with patch('builtins.input', side_effect=KeyboardInterrupt), patch('builtins.print') as output:
    ...     repl(temperature=0)
    >>> output.call_args_list
    [call()]
    """
    chat = Chat()
    try:
        while True:
            user_input = input("chat> ")
            if user_input.startswith('/'):
                print(chat.run_slash(user_input))
            else:
                print(chat.send_message(user_input, temperature=temperature))
    except (KeyboardInterrupt, EOFError):
        print()


if __name__ == "__main__":
    repl()
