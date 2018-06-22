'''An example application that uses ddp_asyncio's MeteorFilesUploader to upload a file to an instance of Meteor-Files' demo application (https://github.com/VeliovGroup/Meteor-Files-Demos)'''

import asyncio
import sys

import logging
logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

from ddp_asyncio import DDPClient
from ddp_asyncio.extras import MeteorFilesUploader

class DemoUploader:
    def __init__(self, address):
        self.client = DDPClient(address)
        self.uploader = MeteorFilesUploader(self.client, 'uploadedFiles')
    
    async def go(self, filename, loop):
        await self.client.connect()
        
        print('Starting upload...')
        
        upload = self.uploader.start_upload(filename, loop = loop, meta = {
            'blamed': 0,
            'secured': False,
            'unlisted': False
        })
        
        while not upload.complete:
            print('{:.1f}% uploaded'.format(upload.progress * 100))
            await asyncio.sleep(1)
        
        print('Upload complete. File ID: {}'.format(upload._id))

du = DemoUploader(sys.argv[1])
loop = asyncio.get_event_loop()
loop.run_until_complete(du.go(sys.argv[2], loop))
