"""A command-line chatbot that talks to a language model."""
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

SYSTEM = "You are a helpful assistant. You always speak like a pirate."


def get_client():
    """Create a Groq client using the API key from the environment."""
    return Groq(api_key=os.environ['GROQ_API_KEY'])


def llm(messages, tools=None, temperature=0.8):
    """Send the conversation to the model and return its reply message."""
    client = get_client()  # created only when a request is made
    response = client.chat.completions.create(
        model='llama-3.1-8b-instant',
        messages=messages,
        tools=tools,
        temperature=temperature,
        timeout=30,
    )
    return response.choices[0].message


class Chat:
    """Hold a conversation history and send messages to the model.

    >>> from unittest.mock import patch
    >>> with patch('chat.get_client') as get_client:
    ...     request = get_client.return_value.chat.completions.create
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

    def __init__(self, system=SYSTEM):
        self.messages = [{"role": "system", "content": system}]

    def send_message(self, message, temperature=0.8):
        """Send a message to the model, keep the reply in history, and return it."""
        self.messages.append({'role': 'user', 'content': message})
        reply = llm(self.messages, temperature=temperature).content
        self.messages.append({'role': 'assistant', 'content': reply})
        return reply


def repl(temperature=0.8):
    """Run the chatbot conversation.

    >>> from unittest.mock import patch, call
    >>> with patch('builtins.input', side_effect=['Hi', 'How are you?', EOFError]), patch('chat.get_client') as get_client, patch('builtins.print') as output:
    ...     request = get_client.return_value.chat.completions.create
    ...     captured = []
    ...     replies = iter(['Hello!', 'Goodbye!'])
    ...     def respond(**kwargs):
    ...         captured.append([m.copy() for m in kwargs['messages']])
    ...         request.return_value.choices[0].message.content = next(replies)
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
            print(chat.send_message(user_input, temperature=temperature))
    except (KeyboardInterrupt, EOFError):
        print()


if __name__ == "__main__":
    repl()
