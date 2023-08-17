#!/usr/bin/env python
from setuptools import setup

try:
    long_description = open('README.md', 'r').read()
except:
    long_description = ''

setup(
    name='baker-python',
    version='1.0.0',
    packages=['baker'],
    url='https://github.com/enginestein/Baker',
    license='GPL-3.0-only',
    author='Arya Praneil Pritesh',
    author_email='aryapraneil@gmail.com',
    install_requires=[],
    description='A framework to create chatbots in the easiest way',
    long_description_content_type='text/markdown',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
    ],
    project_urls={
        'Source': 'https://github.com/enginestein/Baker',
        'Tracker': 'https://github.com/enginestein/Baker',
    },
)
