<h1 id="ddp_asyncio">ddp_asyncio</h1>


<h1 id="ddp_asyncio.ddpclient.DDPClient">DDPClient</h1>

```python
DDPClient(self, url, event_loop=None)
```
Manages a connection to a server.
It takes a URL as the first parameter, the optional second parameter specifies which event loop will be used.

<h2 id="ddp_asyncio.ddpclient.DDPClient.connect">connect</h2>

```python
DDPClient.connect(self)
```
This coroutine establishes a connection to a server. It blocks until the connection is established or an exception is raised.
<h2 id="ddp_asyncio.ddpclient.DDPClient.subscribe">subscribe</h2>

```python
DDPClient.subscribe(self, name, *params)
```
Subscribe to a publication.
subscribe() returns a Subscription object which can be used to monitor the status of the subscription.

<h2 id="ddp_asyncio.ddpclient.DDPClient.unsubscribe">unsubscribe</h2>

```python
DDPClient.unsubscribe(self, sub)
```
Unsubscribe from a publication.
<h2 id="ddp_asyncio.ddpclient.DDPClient.get_collection">get_collection</h2>

```python
DDPClient.get_collection(self, name)
```
Retrieve an existing Collection by name. If the Collection does not exist it will be created.
<h2 id="ddp_asyncio.ddpclient.DDPClient.call">call</h2>

```python
DDPClient.call(self, method, *params)
```
This coroutine calls a remote method on the server and returns the result.
Raises a ddp_asyncio.RemoteMethodError if the server replies with an error.

<h1 id="ddp_asyncio.subscription.Subscription">Subscription</h1>

```python
Subscription(self, name)
```
Tracks the status of a subscription.
The ready property can be used to determine if a subscription is ready.
The error property can be used to determine if a subscription encountered an error.

<h2 id="ddp_asyncio.subscription.Subscription.wait">wait</h2>

```python
Subscription.wait(self)
```
This coroutine waits for the subscription to become ready.
If the server responds with an error then a ddp_asyncio.SubscriptionError will be raised.

<h1 id="ddp_asyncio.collection.Collection">Collection</h1>

```python
Collection(self, name)
```
Stores data published from a connected server.

Collections are read-only and function identically to a dictionary, with each item's _id as the key.

A Collection item's attributes can be accessed like a dictionarie or with dot-notation attribute access, i.e. "item.attr"

<h2 id="ddp_asyncio.collection.Collection.get_queue">get_queue</h2>

```python
Collection.get_queue(self)
```
Creates and returns a new asyncio.Queue to monitor changes to a Collection.
When the collection changes, a CollectionEvent object containing a description of the change is pushed to the queue.

<h1 id="ddp_asyncio.collection.CollectionEvent">CollectionEvent</h1>

```python
CollectionEvent(self, d)
```
Represents a change to a Collection.

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

