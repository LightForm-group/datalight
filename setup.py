#!/usr/bin/env python
import os
from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

package_data = os.path.join('template', '*')

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
      version='0.1.0',
      description=('Data uploader to Zenodo repository for lightform project'),
      long_description=readme,
      author='Nicolas Gruel',
      author_email='nicolas.gruel@manchester.ac.uk',
      url='https://github.com/MechMicroMan/datalight',
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
          'datalight': [package_data],
      },
      include_package_data=True,
      license='MIT',
      plateforms='any'
      )
