#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


import src


setup(

    # le nom de votre bibliothèque, tel qu'il apparaitre sur pypi
    name='population_simulator',
    # la version du code
    version='0.0',

    packages=find_packages(),

    author="edarin, AlexisEidelman",

    # author_email="",

    # Une description courte
    description="Generate a population as close as possible from what we know",

    long_description=open('README.md').read(),

    include_package_data=True,

    url='https://github.com/edarin/population_simulator',


    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],

)
