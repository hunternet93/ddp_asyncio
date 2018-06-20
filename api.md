<h1 id="ddp_asyncio">ddp_asyncio</h1>


<h1 id="ddp_asyncio.ddpclient.DDPClient">DDPClient</h1>

```python
DDPClient(self, url, event_loop=None)
```
Manages a connection to a server.
It takes a URL as the first parameter, the optional second parameter specifies which event loop will be used.

The is_connected property is a boolean which can be used to determine if DDPClient is currently connected to a server.

<h2 id="ddp_asyncio.ddpclient.DDPClient.connect">connect</h2>

```python
DDPClient.connect(self)
```
This coroutine establishes a connection to a server.
It blocks until the connection is established or an exception is raised.

Raises ddp_asyncio.ConnectionError if the server reports a failure (usually caused by incomplatible versions of the DDP protocol.)

<h2 id="ddp_asyncio.ddpclient.DDPClient.disconnect">disconnect</h2>

```python
DDPClient.disconnect(self)
```
Coroutine which disconnects from the server.
Does nothing if called while not connected.

<h2 id="ddp_asyncio.ddpclient.DDPClient.disconnection">disconnection</h2>

```python
DDPClient.disconnection(self)
```
Coroutine that blocks while connected to the server.
<h2 id="ddp_asyncio.ddpclient.DDPClient.get_collection">get_collection</h2>

```python
DDPClient.get_collection(self, name)
```
Retrieve an existing Collection by name. If the Collection does not exist it will be created.
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

