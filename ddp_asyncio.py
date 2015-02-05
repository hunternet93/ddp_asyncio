import asyncio
import websockets
import random
from collections import OrderedDict
import ejson
        
class Subscription:
    def __init__(self, name, added_cb, changed_cb, removed_cb):
        self.id = str(random.randint(0, 1000000))
        self.name = name
        self.data = OrderedDict()
        self.added_cb = added_cb
        self.changed_cb = changed_cb
        self.removed_cb = removed_cb
        
    def sorted(self, key):
        return OrderedDict(sorted(self.data.items(), key=lambda d: d[1][key]))
                
class DDPClient:
    def __init__(self, address):
        self.connected = False
        self.address = address
        
        self.subs = {}
        self.calls = {}
        
    @asyncio.coroutine
    def connect(self):
        print('opening socket')
        self.websocket = yield from websockets.connect(self.address)

        while not self.websocket.open: yield from asyncio.sleep(0.01)
        yield from self.websocket.send(ejson.dumps(
            {
                'msg': 'connect',
                'version': '1',
                'support': ['1']
            }
        ))

        asyncio.get_event_loop().create_task(self.recvloop())
        
    @asyncio.coroutine
    def subscribe(self, name, params = [], added_cb = lambda *a: None,
                  changed_cb = lambda *a: None, removed_cb = lambda *a: None):
        sub = Subscription(name, added_cb, changed_cb, removed_cb)
        self.subs[name] = sub
        yield from self.websocket.send(ejson.dumps(
            {'msg': 'sub',
             'id': sub.id,
             'name': name,
             'params': params}
        ))
        
        return sub

    @asyncio.coroutine        
    def call(self, method, params = [], callback = lambda *a: None):
        id = str(random.randint(1, 1000000))
        self.calls[id] = callback
        yield from self.websocket.send(ejson.dumps(
            {'msg': 'method',
             'method': method,
             'params': params,
             'id': id}
        ))
        
    @asyncio.coroutine
    def recvloop(self):
        while True:
            msg = yield from self.websocket.recv()
            msg = ejson.loads(msg)
            print(msg)
            if msg.get('msg') == 'connected':
                self.connected = True
                print('woo! connected!')
                
            elif msg.get('msg') == 'ping':
                print('pong!')
                yield from self.websocket.send(ejson.dumps({'msg': 'pong', 'id': msg.get('id')}))
                                        
            elif msg.get('msg') == 'added':
                sub = self.subs.get(msg['collection'])
                if sub:
                    sub.data[msg['id']] = msg['fields']
                    sub.added_cb(sub, msg['id'], msg['fields'])
                    
            elif msg.get('msg') == 'changed':
                sub = self.subs.get(msg['collection'])
                if sub:
                    sub.data[msg['id']] = msg['field']
                    sub.changed_cb(sub, msg['id'], msg['fields'])
                    
            elif msg.get('msg') == 'removed':
                sub = self.subs.get(msg['collection'])
                if sub:
                    del sub.data[msg['id']]
                    sub.removed_cb(sub, msg['id'])
                    
            elif msg.get('msg') == 'result':
                call = self.calls.get(msg['id'])
                if call:
                    call(msg.get('result'), msg.get('error'))
