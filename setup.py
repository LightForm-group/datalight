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
      version="0.9.1",
      description='Data uploader to Zenodo repository',
      long_description=readme,
      author='Peter Crowther',
      author_email='peter.crowther-3@manchester.ac.uk',
      url='https://github.com/LightForm-group/datalight',
      keywords=[],
      install_requires=requirements,
      license='MIT',
      )
