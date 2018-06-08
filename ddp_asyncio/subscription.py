import asyncio
import random

from .exceptions import SubscriptionError

class Subscription:
    '''Tracks the status of a subscription.
    The ready property can be used to determine if a subscription is ready.
    The error property can be used to determine if a subscription encountered an error.
    '''
    
    def __init__(self, name):
        self._id = str(random.randint(0, 1000000))
        self._name = name
        
        self.ready = False
        self.error = None
        
        self._ready_event = asyncio.Event()

    def __ready__(self):
        self._ready_event.set()
    
    def __error__(self, error):
        self.error = error
        self._ready_event.set()
        
    async def wait(self):
        '''This coroutine waits for the subscription to become ready.
        If the server responds with an error then a ddp_asyncio.SubscriptionError will be raised.
        '''
        
        await self._ready_event.wait()
        if self.error: raise SubscriptionError(self.error.get('message', self.error))
