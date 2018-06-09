# ddp_asyncio

ddp_asyncio is an asynchronous implementation of [Meteor's DDP protocol](https://github.com/meteor/meteor/blob/devel/packages/ddp/DDP.md) for Python 3.

### Installation

ddp_asyncio isn't on PyPi yet, but will be soon.

Install using the included setup.py script:

    python3 setup.py install

### Usage

[API docs](api.md)

Check out the following examples, all of which use Meteor's reference [Todos](https://github.com/meteor/todos) application.

* [Retrieve todo list](example_retrieve_todos.py)
* [Create a todo list](example_create_todos.py)
* [Watch todo lists for changes](example_watch_todos.py)
