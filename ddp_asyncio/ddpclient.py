import asyncio
import websockets
import random
import ejson

from .subscription import Subscription
from .collection import Collection
from .methodcall import MethodCall
from .exceptions import ConnectionError, NotConnectedError

def ensure_connected(fn):
    '''Decorator which raises ddp_asyncio.NotConnectedError if a function is called when not connected to a server.'''

    def ensure_connected_wrapper(self, *args, **kwargs):
        if not self.is_connected:
            raise NotConnectedError('DDPClient is not connected to a server.')
        
        return fn(self, *args, **kwargs)
    
    return ensure_connected_wrapper
        
class DDPClient:
    '''Manages a connection to a server.
    It takes a URL as the first parameter, the optional second parameter specifies which event loop will be used.
    
    The is_connected property is a boolean which can be used to determine if DDPClient is currently connected to a server.
    '''
    
    def __init__(self, url, event_loop = None):
        self.url = url

        self.is_connected = False
        
        self._websocket = None
        self._event_loop = event_loop or asyncio.get_event_loop()
        self._disconnection_event = asyncio.Event()
        self._disconnection_event.set()
        
        self._subs = {}
        self._cols = {}
        self._calls = {}
        
    async def connect(self):
        '''This coroutine establishes a connection to a server.
        It blocks until the connection is established or an exception is raised.
        
        Raises ddp_asyncio.ConnectionError if the server reports a failure (usually caused by incomplatible versions of the DDP protocol.)
        '''

        self._websocket = await websockets.connect(self.url)
        
        msg = {'msg': 'connect', 'version': '1', 'support': ['1']}
        
        await self._websocket.send(ejson.dumps(msg))

        while self._websocket.open:
            msg = await self._websocket.recv()
            msg = ejson.loads(msg)
            _type = msg.get('msg')
            
            if _type == 'failed':
                raise ConnectionError('The server is not compatible with version 1 of the DDP protocol.')
            elif _type == 'connected':
                # Ensure all Collections are in their default states
                for col in self._cols.values(): col._data = {}
                
                self.is_connected = True
                self._disconnection_event.clear()
                self._event_loop.create_task(self.__handler__())

                return
    
    async def disconnect(self):
        '''Coroutine which disconnects from the server.
        Does nothing if called while not connected.
        '''
        
        if self.is_connected:
            await self._websocket.close()
    
    async def disconnection(self):
        '''Coroutine that blocks while connected to the server.'''
        await self._disconnection_event.wait()
    
    @ensure_connected
    async def subscribe(self, name, *params):
        '''Coroutine that subscribes to a publication.
        subscribe() returns a Subscription object which can be used to monitor the status of the subscription.
        
        Raises ddp_asyncio.NotConnectedError if called while not connected to a server.
        '''
        
        sub = Subscription(name)
        self._subs[sub._id] = sub

        await self._websocket.send(ejson.dumps({
            'msg': 'sub',
            'id': sub._id,
            'name': name,
            'params': params
        }))
        
        return sub
    
    @ensure_connected
    async def unsubscribe(self, sub):
        '''Coroutine that unsubscribes from a publication.
        
        Raises ddp_asyncio.NotConnectedError if called while not connected to a server.
        '''
        
        await self._websocket.send(ejson.dumps({
            'msg': 'unsub',
            'id': sub._id
        }))
    
    def get_collection(self, name):
        '''Retrieve an existing Collection by name. If the Collection does not exist it will be created.'''
        c = self._cols.get(name)

        if not c:
            c = Collection(name)
            self._cols[name] = c

        return c
    
    @ensure_connected
    async def call(self, method, *params):
        '''This coroutine calls a remote method on the server and returns the result.
        
        Raises a ddp_asyncio.RemoteMethodError if the server replies with an error.
        Raises ddp_asyncio.NotConnectedError if called while not connected to a server.
        '''
        
        c = MethodCall()
        self._calls[c._id] = c

        await self._websocket.send(ejson.dumps({
            'msg': 'method',
            'method': method,
            'params': params,
            'id': c._id
        }))
        
        return await c.__wait__()
    
    async def __pong__(self, _id):
        '''Respond to a ping from the server.'''
        await self._websocket.send(ejson.dumps({
            'msg': 'pong',
            'id': _id
        }))
                
    async def __handler__(self):
        '''Handles messages received from the server'''

        while self._websocket.open:
            try:
                msg = await self._websocket.recv()
            except websockets.exceptions.ConnectionClosed:
                break
            
            if not msg: continue

            msg = ejson.loads(msg)
            _type = msg.get('msg')
            
            if _type == 'ping':
                await self.__pong__(msg.get('id'))
                
            elif _type == 'ready':
                for _id in msg['subs']:
                    sub = self._subs.get(_id)
                    if sub: sub.__ready__()
            
            elif _type == 'nosub':
                sub = self._subs.get(msg['id'])
                if sub: sub.__error__(msg.get('error', 'Denied by server for unspecified reason.'))

            elif _type == 'added':
                col = self.get_collection(msg['collection'])
                col.__added__(msg['id'], msg['fields'])
                    
            elif _type == 'changed':
                col = self.get_collection(msg['collection'])
                col.__changed__(msg['id'], msg.get('fields', {}), msg.get('cleared', []))
                    
            elif _type == 'removed':
                col = self.get_collection(msg['collection'])
                col.__removed__(msg['id'])
                    
            elif _type == 'result':
                c = self._calls.get(msg['id'])
                if c:
                    await c.__result__(msg.get('error'), msg.get('result'))
                    del self._calls[msg['id']]
        
        self.is_connected = False
        self._disconnection_event.set()
