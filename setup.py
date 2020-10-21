#!/usr/bin/env python
from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [
    'requests',
    'PyYaml>=5.1',
    'jsonschema',
    'PyQt5'
]

setup(name='datalight',
      packages=['datalight'],
      version=0.8,
      description='Data uploader to Zenodo repository',
      long_description=readme,
      author='Peter Crowther',
      author_email='peter.crowther-3@manchester.ac.uk',
      url='https://github.com/LightForm-group/datalight',
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
      license='MIT',
      )
