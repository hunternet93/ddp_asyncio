import asyncio
import random

from .exceptions import RemoteMethodError

class MethodCall:
    '''An internal representation of a method call'''
    
    def __init__(self):
        self._id = str(random.randint(1, 1000000))
        self._returned = asyncio.Event()
        
        self._error, self._result = None, None
    
    async def __wait__(self):
        await self._returned.wait()
        
        if self._error:
            raise RemoteMethodError(self._error.get('message', self._error))
        else:
            return self._result

    async def __result__(self, error, result):
        self._error, self._result = error, result
        self._returned.set()
