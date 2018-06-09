# ddp_asyncio

ddp_asyncio is an asynchronous implementation of [Meteor's DDP protocol](https://github.com/meteor/meteor/blob/devel/packages/ddp/DDP.md) for Python 3.5+.

### Installation

Install via PyPi:

    pip3 install ddp_asyncio

Or, install using the included setup.py script:

    python3 setup.py install

### Usage

[API docs](https://github.com/hunternet93/ddp_asyncio/blob/master/api.md)

Check out the following examples, all of which use Meteor's reference [Todos](https://github.com/meteor/todos) application.

* [Retrieve todo list](https://github.com/hunternet93/ddp_asyncio/blob/master/example_retrieve_todos.py)
* [Create a todo list](https://github.com/hunternet93/ddp_asyncio/blob/master/example_create_todos.py)
* [Watch todo lists for changes](https://github.com/hunternet93/ddp_asyncio/blob/master/example_watch_todos.py)
