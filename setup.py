#!/usr/bin/env python
# -*- coding: utf-8 -*- #

import setuptools

setuptools.setup(name='lvlss',
                 version='0.0.1',
                 description=u'Once upon a time this was a MUDlike.',
                 long_description=open('README.md').read().strip(),
                 author='Derek Arnold',
                 author_email='derek@derekarnold.net',
                 url='http://github.com/lysol/lvlss',
                 packages=setuptools.find_packages(),
                 scripts=[
                    'src/static/*'
                 ],
                 install_requires=[
                    'flask'
                 ],
                 include_package_data=True,
                 license='MIT License')
