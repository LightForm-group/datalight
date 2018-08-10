#!/usr/bin/env python
import os
import sys
from setuptools import setup
import json

import urllib.request

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

# Obtain the newest version of the licenses definition and replace the one
# provided by the package.
url = 'https://licenses.opendefinition.org/licenses/groups/all.json'
try:
    with urllib.request.urlopen(url) as f:
        licenses = json.load(f)

    _zenodo_path = os.path.join('datalight', 'schemas', 'zenodo')
    with open(os.path.join(_zenodo_path, 'opendefinition-licenses.json'), 'w') as f:
        json.dump(licenses, f)
except urllib.error.URLError:
    print('Licenses file last version not available. '
          'Use the one provided by the package')

requirements = [
    'requests',
    'docopt',
    'pyaml',
    'jsonschema',
]

test_requirements = [
    'pytest',
    'testfixtures',
]

setup(name='datalight',
      packages=['datalight'],
      version='0.5.0',
      description=('Data uploader to Zenodo repository'),
      long_description=readme,
      author='Nicolas Gruel',
      author_email='nicolas.gruel@mgmail.com',
      url='https://github.com/gruel/datalight',
      classifiers=[
          'Development Status :: 1 - RC',
          'Intended Audience :: Science/Research',
          'Topic :: Topic :: Scientific/Engineering :: Physics',
          'Environment :: Console',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Operating System :: Unix',
          'Operating System :: Microsoft',
          'Operating System :: MacOS'
                  ],
      keywords=[],
      install_requires=requirements,
      setup_requires=['pytest-runner'],
      test_suite='test',
      tests_require=test_requirements,
      extra_requires={
          'dev': ['pylint', 'pytest', 'pytest-cov', 'testfixtures', 'coverage'],
          'test': ['pytest', 'pytest-cov', 'testfixtures', 'coverage'],
          'doc': ['sphinx', 'numpydoc']},
      entry_points={
         'console_scripts': [
             ' datalight = datalight.datalight:main']
                   },
      package_data={
          '': ['LICENSE'],
          'datalight': ['schemas/zenodo/metadata-1.0.0.yml',
                        'schemas/zenodo/opendefinition-licenses.json'],
      },
      include_package_data=True,
      license='MIT',
      plateforms='any'
      )
