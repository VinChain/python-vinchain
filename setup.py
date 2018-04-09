#!/usr/bin/env python3

from setuptools import setup

# Work around mbcs bug in distutils.
# http://bugs.python.org/issue10945
import codecs
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    codecs.register(lambda name, enc=ascii: {True: enc}.get(name == 'mbcs'))

VERSION = '0.1.12'

setup(
    name='vinchainio',
    version=VERSION,
    description='Python library for vinchain.io',
    long_description=open('README.md').read(),
    author='Vinchain.io',
    author_email='info@vinchain.io',
    maintainer='Vinchain.io',
    maintainer_email='info@vinchain.io',
    url='http://vinchain.io',
    keywords=['vinchain.io', 'library', 'api', 'rpc'],
    packages=[
        "vinchainio",
        "vinchainioapi",
        "vinchainiobase",
        "grapheneapi",
        "graphenebase",
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial',
    ],
    install_requires=[
        "appdirs",
        "ecdsa",
        "Events",
        "pycryptodome",  # for AES, installed through graphenelib already
        "pylibscrypt",
        "requests",
        "scrypt",
        "websocket-client",
        "websockets",
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    include_package_data=True,
)
