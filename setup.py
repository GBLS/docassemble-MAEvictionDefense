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
      version='0.1.12',
      description=('A guided interview for pro se eviction defense in Massachusetts. Generates an Answer form, Request for Discovery, and accompanying forms and motions.'),
      long_description=u"# docassemble.MAEvictionDefense\r\n\r\nA guided interview for pro se eviction defense in Massachusetts. Generates an Answer form, \r\nRequest for Discovery, and accompanying forms and motions.\r\n## Changelog\r\n\r\n* 2019-02-12 Fix survey link\r\n* 2019-02-11 Layout improvements for initial screen; bugfixes  \r\n* 2019-02-11 Migrate to object-based MACourts module with complete court list\r\n* 2019-02-01 Bugfixes\r\n* 2019-01-20 Language improvements from court\r\n* 2019-01-16 Bugfixes\r\n* 2019-01-11 Error with late answer date calculation\r\n* 2018-12-27 First version with complete Spanish language translation\r\n* 2018-12-26 Bug fixes. Added survey email\r\n* 2018-12-19 Bug fixes / language improvements suggested by court staff\r\n* 2018-12-16 urgent bug fix with illegal characters in download filename\r\n* 2018-12-15 Improved language, handle compel discovery form better if user is not going to return to online interview\r\n* 2018-12-13 Added clinic feature, slight language cleanup and require date_received_ntq if it is known\r\n* 2018-12-10 Fix bug w/ landlord's attorney's name\r\n* 2018-12-04 Many improvements to language and workflow suggested by attorney/advocate feedback. New interpreter notice\r\n* 2018-11-06 Added sharing menu link, support signing on phones\r\n* 2018-11-04 Remove Evacuation Day -- not observed by courts\r\n* 2018-11-03 Account for holidays. New cover sheet designed by Rina\r\n* 2018-11-01 Fixed regression: restored SMS messaging, bug on nonpayment of rent cure\r\n* 2018-10-29 Began groundwork for Spanish translation; bugfixes and major reorganization\r\n* 2018-10-24 Bugfix (additional fields required but hidden)\r\n* 2018-10-24 Bugfix (foreclosure field required). Groundwork for separate motion to compel\r\n* 2018-10-19 Worked on interview flow and hid more irrelevant questions\r\n* 2018-10-18 Added condo conversion defense. Enhanced discovery. Language and review screen cleanup\r\n* 2018-10-11 Added experimental support for reviewing and editing answers (~ 80% coverage)\r\n* 2018-10-04 / 2018-10-05 Bug fixes-security deposit, replace URLs so not blocked by SMS spam measures\r\n* 2018-08-18 Explain discovery to pro se users, review initial defenses, add detail to answer\r\n* 2018-08-17 Email reminders, compact attachments page and wording / help improvements\r\n* 2018-07-08 Bug fixes\r\n* 2018-07-01 Added videos created by MLRI\r\n\r\n## Contributors:\r\n    \r\n1. Quinten Steenhuis, Esq. ([Greater Boston Legal Services](https://www.gbls.org))\r\n1. Rina Padua ([Greater Boston Legal Services](https://www.gbls.org) and Harvard University [Phillips Brooks House](http://pbha.org/))\r\n1. Caroline Robinson ([Massachusetts Law Reform Institute](http://www.mlri.org))\r\n1. Mariah Jennings-Rampsi, Esq. ([Volunteer Lawyer's Project](https://www.vlpnet.org/))\r\n",
      long_description_content_type='text/markdown',
      author='Quinten Steenhuis, Greater Boston Legal Services',
      author_email='qsteenhuis@gbls.org',
      license='MIT',
      url='https://www.gbls.org',
      packages=find_packages(),
      namespace_packages=['docassemble'],
      install_requires=['docassemble.MACourts', 'dt-send-answers', 'holidays'],
      zip_safe=False,
      package_data=find_package_data(where='docassemble/MAEvictionDefense/', package='docassemble.MAEvictionDefense'),
     )

