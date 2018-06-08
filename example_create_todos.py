'''An example application that uses ddp_asyncio to add a to-do list to Meteor's reference Todos application (https://github.com/meteor/todos)'''

import asyncio
import sys

from ddp_asyncio import DDPClient

class TodoCreator:
    def __init__(self, address):
        self.client = DDPClient(address)
    
    async def go(self):
        await self.client.connect()
        
        list_id = await self.client.call('lists.insert', {'language': 'en'})
        await self.client.call('lists.updateName', {'listId': list_id, 'newName': 'List created via ddp_asyncio!'})
        
        todo_id = await self.client.call('todos.insert', {'listId': list_id, 'text': "Isn't that pretty cool?"})
        

td = TodoCreator(sys.argv[1])
asyncio.get_event_loop().run_until_complete(td.go())
