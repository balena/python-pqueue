#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='pqueue',
    version=__import__('pqueue').__version__,
    description=(
        'A single process, persistent multi-producer, multi-consumer queue.'
    ),
    long_description=open('README.rst').read(),
    author='G. B. Versiani',
    author_email='guibv@yahoo.com',
    maintainer='G. B. Versiani',
    maintainer_email='guibv@yahoo.com',
    license='BSD',
    packages=find_packages(),
    platforms=["all"],
    url='http://github.com/balena/python-pqueue',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries'
    ],
    test_suite = 'runtests.runtests',
)
