import asyncio
import websockets
import random
import ejson

from .subscription import Subscription
from .collection import Collection
from .methodcall import MethodCall
from .exceptions import ConnectionError
        
class DDPClient:
    '''Manages a connection to a server.
    It takes a URL as the first parameter, the optional second parameter specifies which event loop will be used.
    '''
    
    def __init__(self, url, event_loop = None):
        self.connected = False
        self.url = url
        
        self._websocket = None
        self._session = None
        self._event_loop = event_loop or asyncio.get_event_loop()
        
        self._subs = {}
        self._cols = {}
        self._calls = {}
        
    async def connect(self):
        '''This coroutine establishes a connection to a server. It blocks until the connection is established or an exception is raised.'''

        self._websocket = await websockets.connect(self.url)
        
        msg = {'msg': 'connect', 'version': '1', 'support': ['1']}
        if self._session:
            # If we were previously connected, we can attempt to resume that session
            msg['session'] = self._session

        await self._websocket.send(ejson.dumps(msg))

        while self._websocket.open:
            msg = await self._websocket.recv()
            msg = ejson.loads(msg)
            _type = msg.get('msg')
            
            if _type == 'failed':
                raise ConnectionError('The server is not compatible with version 1 of the DDP protocol.')
            elif _type == 'connected':
                self.connected = True
                self._session = msg['session']
            
                self._event_loop.create_task(self.__handler__())

                return
    
    async def disconnect(self):
        await self._websocket.close()
        self.connected = False
        
    async def subscribe(self, name, *params):
        '''Subscribe to a publication.
        subscribe() returns a Subscription object which can be used to monitor the status of the subscription.
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
    
    async def unsubscribe(self, sub):
        '''Unsubscribe from a publication.'''
        
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
    
    async def call(self, method, *params):
        '''This coroutine calls a remote method on the server and returns the result.
        Raises a ddp_asyncio.RemoteMethodError if the server replies with an error.
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
