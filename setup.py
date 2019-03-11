#!/usr/bin/env python
from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [
    'requests',
    'PyYaml',
    'jsonschema',
]

test_requirements = [
    'pytest',
]

setup(name='datalight',
      packages=['datalight'],
      version=0.7,
      description='Data uploader to Zenodo repository',
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
      entry_points={
         'console_scripts': [
             ' datalight = datalight.datalight:main']
                   },
      package_data={
          '': ['LICENSE'],
          'datalight': ['schemas/zenodo/zenodo_upload_metadata_schema.json5',
                        'schemas/zenodo/opendefinition-licenses.json'],
      },
      include_package_data=True,
      license='MIT',
      )
