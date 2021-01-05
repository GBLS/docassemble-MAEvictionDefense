import os
import sys
from setuptools import setup, find_packages
from fnmatch import fnmatchcase
from distutils.util import convert_path

standard_exclude = ('*.pyc', '*~', '.*', '*.bak', '*.swp*')
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
      version='0.1.92',
      description=('A guided interview for pro se eviction defense in Massachusetts. Generates an Answer form, Request for Discovery, and accompanying forms and motions.'),
      long_description='# docassemble.MAEvictionDefense\r\n\r\nA guided interview for pro se eviction defense in Massachusetts, using the project\r\nname MADE, Massachusetts Defense for Eviction. Generates an Answer form, \r\nRequest for Discovery, and accompanying forms and motions.\r\n\r\n## Changelog\r\n\r\n* 2020-01-05 Bug fix when using new attorney name\r\n* 2020-01-04 Add support for attorney entering appearance\r\n* 2020-01-03 Integrate language files\r\n* 2020-12-10 Edit additional tenant signature\r\n* 2020-12-02 Language tweaks, compatibility with docassemble 1.2.7\r\n* 2020-11-18 Translate section labels\r\n* 2020-11-17 Integrate feedback from housing coalition\r\n* 2020-11-14 New feedback form that creates Github issues\r\n* 2020-11-13 Added CARES/CDC language to Answer\r\n* 2020-11-09 Update language to reflect Housing Court standing order 6-20\r\n* 2020-10-14 Integrate Tyler videos\r\n* 2020-09-18 Improved Spanish translation/added Spanish videos\r\n* 2020-08-18 Incorporate non-essential eviction defenses/discovery\r\n* 2020-08-10 Make save/load answers easier to see; highlight sign-in link\r\n* 2020-07-28 Update gbls_intake.py to account for breaking change upstream\r\n* 2020-07-27 Added Covid-19 language\r\n* 2020-03-16 Fix incorrect indentation in text reminder\r\n* 2020-03-02 Explicitly list Boston neighborhoods for GBLS intake\r\n* 2020-02-20 Added first draft of optional additional defendants\r\n* 2020-02-18 Tweaks to intake case preview\r\n* 2020-01-20 No longer show "Anonymous User" if someone is not logged in\r\n* 2020-01-07 Better intake (require contact info), updated Spanish translation\r\n* 2019-12-17 Improved signature page\r\n* 2019-12-04 Additional efforts to reduce resource exhaustion. Add intake to GBLS\'s Legal Server instance\r\n* 2019-11-27 stagger survey emails; other cron randomization to reduce risk of resource exhaustion\r\n* 2019-11-25 Added survey link; fix Monday holiday problem; language fixes\r\n* 2019-08-12 Fixed bug with MRVP\r\n* 2019-08-09 Language fixes\r\n* 2019-08-07 Language fixes\r\n* 2019-08-02 Language fixes\r\n* 2019-07-12 Language fixes\r\n* 2019-06-26 Added 4 new languages: Vietnamese, Haitian Creole, Chinese (Traditional) and Portuguese\r\n* 2019-06-04 Language translation prep\r\n* 2019-05-28 Added question IDs\r\n* 2019-05-01 Improved instructions for discovery requests\r\n* 2019-03-25 Cleaned up instructions, bugfixes\r\n* Bugfix - ls_email\r\n* Test\r\n* 2019-02-18 Bugfixes (transition to new MACourt object)\r\n* 2019-02-14 Bugfixes\r\n* 2019-02-14 Resolve bugs in Spanish language version (unicode errors)\r\n* 2019-02-12 Fix survey link\r\n* 2019-02-11 Layout improvements for initial screen; bugfixes  \r\n* 2019-02-11 Migrate to object-based MACourts module with complete court list\r\n* 2019-02-01 Bugfixes\r\n* 2019-01-20 Language improvements from court\r\n* 2019-01-16 Bugfixes\r\n* 2019-01-11 Error with late answer date calculation\r\n* 2018-12-27 First version with complete Spanish language translation\r\n* 2018-12-26 Bug fixes. Added survey email\r\n* 2018-12-19 Bug fixes / language improvements suggested by court staff\r\n* 2018-12-16 urgent bug fix with illegal characters in download filename\r\n* 2018-12-15 Improved language, handle compel discovery form better if user is not going to return to online interview\r\n* 2018-12-13 Added clinic feature, slight language cleanup and require date_received_ntq if it is known\r\n* 2018-12-10 Fix bug w/ landlord\'s attorney\'s name\r\n* 2018-12-04 Many improvements to language and workflow suggested by attorney/advocate feedback. New interpreter notice\r\n* 2018-11-06 Added sharing menu link, support signing on phones\r\n* 2018-11-04 Remove Evacuation Day -- not observed by courts\r\n* 2018-11-03 Account for holidays. New cover sheet designed by Rina\r\n* 2018-11-01 Fixed regression: restored SMS messaging, bug on nonpayment of rent cure\r\n* 2018-10-29 Began groundwork for Spanish translation; bugfixes and major reorganization\r\n* 2018-10-24 Bugfix (additional fields required but hidden)\r\n* 2018-10-24 Bugfix (foreclosure field required). Groundwork for separate motion to compel\r\n* 2018-10-19 Worked on interview flow and hid more irrelevant questions\r\n* 2018-10-18 Added condo conversion defense. Enhanced discovery. Language and review screen cleanup\r\n* 2018-10-11 Added experimental support for reviewing and editing answers (~ 80% coverage)\r\n* 2018-10-04 / 2018-10-05 Bug fixes-security deposit, replace URLs so not blocked by SMS spam measures\r\n* 2018-08-18 Explain discovery to pro se users, review initial defenses, add detail to answer\r\n* 2018-08-17 Email reminders, compact attachments page and wording / help improvements\r\n* 2018-07-08 Bug fixes\r\n* 2018-07-01 Added videos created by MLRI\r\n\r\n## Contributors:\r\n    \r\n1. Quinten Steenhuis, Esq. ([Greater Boston Legal Services](https://www.gbls.org))\r\n1. Rina Padua ([Greater Boston Legal Services](https://www.gbls.org) and Harvard University [Phillips Brooks House](http://pbha.org/))\r\n1. Caroline Robinson ([Massachusetts Law Reform Institute](http://www.mlri.org))\r\n1. Mariah Jennings-Rampsi, Esq. ([Volunteer Lawyer\'s Project](https://www.vlpnet.org/))\r\n',
      long_description_content_type='text/markdown',
      author='Quinten Steenhuis, Greater Boston Legal Services',
      author_email='qsteenhuis@gbls.org',
      license='MIT',
      url='https://www.gbls.org',
      packages=find_packages(),
      namespace_packages=['docassemble'],
      install_requires=['docassemble.MACourts>=0.0.47', 'docassemble.income>=0.0.33'],
      zip_safe=False,
      package_data=find_package_data(where='docassemble/MAEvictionDefense/', package='docassemble.MAEvictionDefense'),
     )

