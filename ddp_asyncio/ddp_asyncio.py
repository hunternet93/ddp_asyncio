import asyncio
import websockets
import random
from collections import OrderedDict
import ejson

@asyncio.coroutine
def noop(*a): return

class RemoteMethodError(Exception):
    pass
        
class Subscription:
    def __init__(self, name, ready_cb, added_cb, changed_cb, removed_cb):
        self.id = str(random.randint(0, 1000000))
        self.name = name
        self.data = OrderedDict()
        self.ready_cb = ready_cb
        self.added_cb = added_cb
        self.changed_cb = changed_cb
        self.removed_cb = removed_cb
        
    def sorted(self, key):
        return OrderedDict(sorted(self.data.items(), key=lambda d: d[1][key]))
        
class MethodCall:
    def __init__(self, callback):
        self.id = str(random.randint(1, 1000000))
        self.callback = callback
        self.finished = False
        self.result, self.error = None, None

    @asyncio.coroutine        
    def onfinished(self, result, error):
        self.finished = True
        self.result, self.error = result, error

        if error:
            raise RemoteMethodError(error['error'])

        if self.callback:
            yield from self.callback(result)
                
class DDPClient:
    def __init__(self, address):
        self.connected = False
        self.address = address
        self.session = None
        
        self.subs = {}
        self.calls = {}
        
        self.callcache = []
        
    @asyncio.coroutine
    def connect(self):
        c = False
        while not c:
            try:
                self.websocket = yield from websockets.connect(self.address)
                c = self.websocket.open
                print(c)
            except ConnectionRefusedError:
                yield from asyncio.sleep(1)
        
        msg = {'msg': 'connect', 'version': '1', 'support': ['1']}
        if self.session: msg['session'] = self.session
        yield from self.websocket.send(ejson.dumps(msg))

        asyncio.async(self.recvloop())
        while not self.connected:
            yield from asyncio.sleep(0.1)
        
    @asyncio.coroutine
    def subscribe(self, name, *params, ready_cb = noop,
                  added_cb = noop, changed_cb = noop, removed_cb = noop):
        sub = Subscription(name, ready_cb, added_cb, changed_cb, removed_cb)
        self.subs[name] = sub
        yield from self.websocket.send(ejson.dumps(
            {'msg': 'sub',
             'id': sub.id,
             'name': name,
             'params': params}
        ))
        
        return sub

    @asyncio.coroutine        
    def call(self, method, *params, callback = None, wait = True):
        c = MethodCall(callback)
        self.calls[c.id] = c

        yield from self.websocket.send(ejson.dumps(
            {'msg': 'method',
             'method': method,
             'params': params,
             'id': c.id}
        ))
        
        if wait:
            while not c.finished:
                yield from asyncio.sleep(0.1)
                
            return c.result
        
    @asyncio.coroutine
    def call_cached(self, method, params = [], callback = lambda *a: None):
        if self.connected:
            yield from self.call(method, params, callback)
        else:
            self.callcache.append((method, params, callback))
        
    @asyncio.coroutine
    def recvloop(self):
        while self.websocket.open:
            while len(self.callcache) > 0:
                self.call(*self.callcache.pop(0))
            
            msg = yield from self.websocket.recv()
            if not msg: continue
            msg = ejson.loads(msg)

            if msg.get('msg') == 'connected':
                self.connected = True
                self.session = msg['session']
                
            elif msg.get('msg') == 'ping':
                yield from self.websocket.send(ejson.dumps({'msg': 'pong', 'id': msg.get('id')}))
                
            elif msg.get('msg') == 'ready':
                for sub in self.subs.values():
                    if sub.id in msg['subs']:
                        yield from sub.ready_cb(sub)

            elif msg.get('msg') == 'added':
                sub = self.subs.get(msg['collection'])
                if sub:
                    sub.data[msg['id']] = msg['fields']
                    yield from sub.added_cb(sub, msg['id'], msg['fields'])
                    
            elif msg.get('msg') == 'changed':
                sub = self.subs.get(msg['collection'])
                if sub:
                    if msg.get('fields'):
                        sub.data[msg['id']].update(msg['fields'])
                        yield from sub.changed_cb(sub, msg['id'], msg['fields'])
                    elif msg.get('cleared'):
                        for key in msg['cleared']:
                            del sub.data[key]
                        yield from sub.changed_cb(sub, msg['id'], msg['cleared'])
                    
            elif msg.get('msg') == 'removed':
                sub = self.subs.get(msg['collection'])
                if sub:
                    del sub.data[msg['id']]
                    yield from sub.removed_cb(sub, msg['id'])
                    
            elif msg.get('msg') == 'result':
                c = self.calls.get(msg['id'])
                if c:
                    yield from c.onfinished(msg.get('result'), msg.get('error'))
                    
        self.connected = False
        while True:
            yield from self.connect()
            return

