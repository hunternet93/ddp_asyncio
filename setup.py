from setuptools import setup, find_packages

setup(
    name='ddp_asyncio',
    version='0.0.1',
    description='Asynchronous DDP library',
    long_description='A library for interfacing with servers using the DDP protocol (such as Meteor) asynchronously using the asyncio library.',
    url='https://github.com/hunternet93/ddp_asyncio',

    author='Isaac Smith',
    author_email='isaac@isrv.pw',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords='ddp meteor',

    packages=find_packages(),
    install_requires=['websockets', 'ejson'],
)
