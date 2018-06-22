import os
import uuid
import math
import base64

import asyncio
import aiohttp

import mimetypes
import urllib.parse

class MeteorFilesException(Exception): pass

class MeteorFilesUploader:
    '''Uploads files to a Meteor-Files collection via HTTP (https://github.com/VeliovGroup/Meteor-Files)'''
    
    def __init__(self, client, collection_name):
        self.client = client
        self.collection_name = collection_name
    
    def start_upload(self, file_or_path, name = None, mimetype = None, meta = {}, loop = asyncio.get_event_loop()):
        '''Starts the upload of a file to this uploader's Meteor-Files collection.
        
        The file_or_path argument may be a file-like object or a file path. If a file-like object is provided, the name argument must be provided as well.
        If a mimetype is not provided it will be guessed from the file's extension. A MeteorFilesException will be raised if mimetype cannot be determined.
        The meta property may be any JSON-encodable object and will be passed to the server along with the file.
        The loop property may be set to an ayncio event loop. If not set, the default will be used.
        
        Returns an Upload object which can be used to monitor the upload.
        '''
        
        return Upload(self, file_or_path, name, mimetype, meta, loop)

class Upload:
    '''Tracks an in-progress upload.
    
    The _id property contains the uploaded file's ID in the target collection.
    The progress property states the progress of the upload as a float between 0 and 1.
    The completed property states if the upload is complete as a boolean.
    '''
    
    def __init__(self, uploader, file_or_path, name, mimetype, meta, loop):
        self.client = uploader.client
        self.collection_name = uploader.collection_name
        
        self._id = str(uuid.uuid4())
        
        if type(file_or_path) == str:
            if not name: name = os.path.basename(file_or_path)
            self.file = open(file_or_path, 'rb')
        
        else:
            if not name:
                raise MeteorFilesException('The name argument must be provided when calling upload() with a file-like object.')
            
            self.file = file_or_path
        
        self.name = name
        
        if not mimetype:
            mimetype = mimetypes.guess_type(name)[0]
            if not mimetype:
                raise MeteorFilesException('Could not determine mimetype of the specified file.')
        
        self.mimetype = mimetype

        self.filesize = os.stat(self.file.fileno()).st_size

        self.meta = meta

        self.progress = 0
        self.complete = False
        
        self._complete_event = asyncio.Event()
        self._canceled = False
        
        self._upload_task = loop.create_task(self.__do_upload__())
    
    async def wait(self):
        '''Coroutine that waits until this upload is complete.'''
        await self._complete_event()        
    
    async def __do_upload__(self):
        chunk_size = 1048576 # No idea.
        chunk_count = int(math.ceil(self.filesize / chunk_size)) or 1
        
        upload_info = await self.client.call(
            '_FilesCollectionStart_{}'.format(self.collection_name),
            {
                'file': {
                    'name': self.name,
                    'type': self.mimetype,
                    'size': self.filesize,
                    'meta': self.meta
                },
                'fileId': self._id,
                'chunkSize': chunk_size,
                'fileLength': chunk_count
            },
            True
        )
        
        parsed = urllib.parse.urlparse(self.client.url)
        upload_uri = '{}://{}{}'.format(
            'https' if parsed.scheme is 'wss' else 'http',
            parsed.netloc,
            upload_info['uploadRoute']
        )
        
        async with aiohttp.ClientSession() as session:
            for chunk_id in range(chunk_count):
                chunk = base64.b64encode(self.file.read(chunk_size))

                await session.post(upload_uri, data = chunk, headers = {
                    'x-eof': '0',
                    'x-fileId': self._id,
                    'x-chunkId': str(chunk_id + 1),
                    'Content-Type': self.mimetype
                })
                
                self.progress = chunk_id / chunk_count
            
            await session.post(upload_uri, data = '', headers = {
                'x-eof': '1',
                'x-fileId': self._id,
                'Content-Type': 'text/plain'
            })
            
        self.progress = 1
        self.complete = True
        
        self.file.close()
