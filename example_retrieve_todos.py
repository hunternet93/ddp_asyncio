'''An example application that uses ddp_asyncio to retrieve all public to-do lists from Meteor's reference Todos application (https://github.com/meteor/todos)'''

import asyncio
import sys

from ddp_asyncio import DDPClient

class TodoRetriever:
    def __init__(self, address):
        self.client = DDPClient(address)
    
    async def go(self):
        await self.client.connect()
        
        lists = self.client.get_collection('lists')
        todos = self.client.get_collection('todos')
        
        sub = await self.client.subscribe('lists.public')
        await sub.wait()
        
        lists_sorted = sorted(lists.values(), key = lambda l: l.name)
        for l in lists_sorted:
            sub = await self.client.subscribe('todos.inList', {'listId': l._id})
            await sub.wait()
            
            print(l.name)
            
            for todo in filter(lambda t: t.listId == l._id, todos.values()):
                print('    [{}] {}'.format('X' if todo.checked else ' ', todo.text))
            
            print()


td = TodoRetriever(sys.argv[1])
asyncio.get_event_loop().run_until_complete(td.go())
