from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='ddp_asyncio',
    version='0.2.0',
    description='Asynchronous DDP library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hunternet93/ddp_asyncio',
    download_url='https://github.com/hunternet93/ddp_asyncio/releases/download/0.2.0/ddp_asyncio-0.2.0.tar.gz',

    author='Isaac Smith',
    author_email='isaac@isrv.pw',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',
        
        'Operating System :: OS Independent',

        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        
        'Framework :: AsyncIO'
    ],

    keywords='ddp meteor',
    packages=find_packages(),
    install_requires=['websockets', 'ejson'],
)
