#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests[security]==2.9.1',
    'beautifulsoup4==4.4.1',
    'Click==6.3',
    'pytimeparse==1.1.5',
    'Pillow==3.1.1',
    'html5lib==0.9999999',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='imageporndirtyrubot',
    version='0.1.0',
    description="Dirty.ru bot",
    long_description=readme + '\n\n' + history,
    author="Ilya Tikhonov",
    author_email='ili.tikhonov@gmail.com',
    url='https://github.com/piha/imageporndirtyrubot',
    packages=[
        'imageporndirtyrubot',
    ],
    package_dir={'imageporndirtyrubot':
                 'imageporndirtyrubot'},
    include_package_data=True,
    install_requires=requirements,
    entry_points='''
        [console_scripts]
        imageporndirtyrubot=imageporndirtyrubot.dirtybot:imageporndirtyrubot
    ''',
    license="ISCL",
    zip_safe=False,
    keywords='imageporndirtyrubot',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
