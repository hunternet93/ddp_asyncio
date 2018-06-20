'''An example application that uses ddp_asyncio to watch all public to-do lists from Meteor's reference Todos application (https://github.com/meteor/todos)'''

import asyncio
import sys

from ddp_asyncio import DDPClient

class TodoWatcher:
    def __init__(self, address):
        self.client = DDPClient(address)
        
        self.lists_subs = {}
    
    async def watch_lists(self, lists, lists_q):
        while True:
            event = await lists_q.get()
            
            if event.type == 'added':
                print('List created: "{}"'.format(event.fields.name))

                sub = await self.client.subscribe('todos.inList', {'listId': event._id})
                self.lists_subs[event._id] = sub
            
            elif event.type == 'changed':
                if event.fields.get('name'):
                    print('List renamed to "{}"'.format(event.fields.name))
            
            elif event.type == 'removed':
                print('List deleted: "{}"'.format(event._id))
                
                await self.client.unsubscribe(self.lists_subs[event._id])
                del self.lists_subs[event._id]

    async def watch_todos(self, todos, todos_q):
        while True:
            event = await todos_q.get()
            
            if event.type == 'added':
                print('Task created: "{}"'.format(event.fields.text))
            
            elif event.type == 'changed':
                if event.fields.get('name'):
                    print('Task changed to "{}"'.format(event.fields.text))
                
                if not event.fields.get('checked') == None:
                    if event.fields.checked:
                        print('Task marked complete: "{}"'.format(todos[event._id].text))
                    else:
                        print('Task marked incomplete: "{}"'.format(todos[event._id].text))
            
            elif event.type == 'removed':
                print('Task deleted: "{}"'.format(event._id))

    async def go(self, loop):
        print('Connecting to server...')
        
        while True:
            try:
                session = await self.client.connect()
            except ConnectionRefusedError or ConnectionResetError:
                await asyncio.sleep(1)
                continue
            
            print('Connected to server.')
            
            lists = self.client.get_collection('lists')
            lists_q = lists.get_queue()
            lists_task = loop.create_task(self.watch_lists(lists, lists_q))
            
            todos = self.client.get_collection('todos')
            todos_q = todos.get_queue()
            todos_task = loop.create_task(self.watch_todos(todos, todos_q))
            
            sub = await self.client.subscribe('lists.public')
            await sub.wait()
            
            await self.client.disconnection()
            print('Lost connection to server, attempting to reestablish...')
            
            lists_task.cancel()
            todos_task.cancel()

loop = asyncio.get_event_loop()

td = TodoWatcher(sys.argv[1])

loop.run_until_complete(td.go(loop))
