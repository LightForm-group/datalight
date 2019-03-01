#!/usr/bin/env python
import os
import sys
from setuptools import setup
import json

import urllib.request

from datalight.__init__ import __version__

with open('README.rst') as readme_file:
    readme = readme_file.read()

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
    'PyYaml',
    'jsonschema',
]

test_requirements = [
    'pytest',
]

setup(name='datalight',
      packages=['datalight'],
      version=__version__,
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
          'dev': ['pylint', 'pytest', 'pytest-cov', 'coverage'],
          'test': ['pytest', 'pytest-cov', 'coverage'],
          'doc': ['sphinx', 'numpydoc']},
      entry_points={
         'console_scripts': [
             ' datalight = datalight.datalight:main']
                   },
      package_data={
          '': ['LICENSE'],
          'datalight': ['schemas/zenodo/record-1.0.0.yml',
                        'schemas/zenodo/opendefinition-licenses.json'],
      },
      include_package_data=True,
      license='MIT',
      plateforms='any'
      )
