import collections
import asyncio
import random
import weakref

from .dotable import Dotable

class CollectionEvent(Dotable):
    '''Represents a change to a Collection.
    
    There are three types of changes: additions, changes, and removals. The type property states the type of change that occurred. 
    
    Additions have the following properties:
        type: 'added'
        _id: id of added item
        fields: contents of added item
    The fields property can be accessed like a dictionary or using dot-notation attribute access.
    
    Changes have the following properties:
        type: 'changed'
        _id: id of changed item
        fields: contents of changed item
        cleared: list of keys removed from the item
    
    Removals have the following properties:
        type: 'removed'
        _id: id of removed item
    '''
    pass

# Note: Collection does not currently support ordered collections, since Meteor doesn't use them.

class Collection(collections.Mapping):
    '''Stores data published from a connected server.

    Collections are read-only and function identically to a dictionary, with each item's _id as the key.

    A Collection item's attributes can be accessed like a dictionarie or with dot-notation attribute access, i.e. "item.attr"
    '''

    def __init__(self, name):
        self._name = name
        self._data = {}

        self._queues = set()

    def __getitem__(self, key):
        return self._data[key]
    
    def __len__(self):
        return len(self._data)
    
    def __iter__(self):
        return iter(self._data)
    
    def __bool__(self):
        return True
    
    def __repr__(self):
        return '<collection {}>'.format(self._name)

    def get_queue(self):
        '''Creates and returns a new asyncio.Queue to monitor changes to a Collection.
        When the collection changes, a CollectionEvent object containing a description of the change is pushed to the queue.
        '''
        
        q = asyncio.Queue()
        self._queues.add(weakref.ref(q))
        return q

    def __put__(self, data):
        for ref in self._queues:
            q = ref()
            if q: q.put_nowait(data)

    def __added__(self, _id, fields):
        self._data[_id] = Dotable.parse(fields)
        self._data[_id]['_id'] = _id
        
        self.__put__(CollectionEvent({
            'type': 'added',
            '_id': _id,
            'fields': Dotable.parse(fields)
        }))
    
    def __changed__(self, _id, fields, cleared):
        if fields:
            self._data[_id].update(fields)
        elif cleared:
            for key in cleared:
                del self._data[_id][key]
        
        self.__put__(CollectionEvent({
            'type': 'changed',
            '_id': _id,
            'fields': Dotable.parse(fields),
            'cleared': cleared
        }))
    
    def __removed__(self, _id):
        del self._data[_id]
        
        self.__put__(CollectionEvent({
            'type': 'removed',
            '_id': _id
        }))
