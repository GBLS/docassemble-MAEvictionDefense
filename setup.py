#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages
from fnmatch import fnmatchcase
from distutils.util import convert_path

standard_exclude = ('*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build', './dist', 'EGG-INFO', '*.egg-info')
def find_package_data(where='.', package='', exclude=standard_exclude, exclude_directories=standard_exclude_directories):
    out = {}
    stack = [(convert_path(where), '', package)]
    while stack:
        where, prefix, package = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                        stack.append((fn, '', new_package))
                else:
                    stack.append((fn, prefix + name + '/', package))
            else:
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

setup(name='docassemble.MAEvictionDefense',
      version='0.0.44',
      description=('A guided interview for pro se eviction defense in Massachusetts. Generates an Answer form, Request for Discovery, and accompanying forms and motions.'),
      long_description="# docassemble.MAEvictionDefense\r\n\r\nA guided interview for pro se eviction defense in Massachusetts. Generates an Answer form, \r\nRequest for Discovery, and accompanying forms and motions.\r\n## Changelog\r\n2018-08-18 Explain discovery to pro se users, review initial defenses, add detail to answer\r\n2018-08-17 Email reminders, compact attachments page and wording / help improvements\r\n2018-07-08 Bug fixes\r\n2018-07-01 Added videos created by MLRI\r\n\r\n## Contributors:\r\n    \r\n1. Quinten Steenhuis, Esq. ([Greater Boston Legal Services](https://www.gbls.org))\r\n1. Rina Padua ([Greater Boston Legal Services](https://www.gbls.org) and Harvard University [Phillips Brooks House](http://pbha.org/))\r\n1. Caroline Robinson ([Massachusetts Law Reform Institute](http://www.mlri.org))\r\n1. Mariah Jennings-Rampsi, Esq. ([Volunteer Lawyer's Project](https://www.vlpnet.org/))\r\n",
      long_description_content_type='text/markdown',
      author='Quinten Steenhuis, Greater Boston Legal Services',
      author_email='qsteenhuis@gbls.org',
      license='MIT',
      url='https://www.gbls.org',
      packages=find_packages(),
      namespace_packages=['docassemble'],
      install_requires=[],
      zip_safe=False,
      package_data=find_package_data(where='docassemble/MAEvictionDefense/', package='docassemble.MAEvictionDefense'),
     )

