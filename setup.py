from setuptools import setup


with open('README.rst') as readme_file:
        README = readme_file.read()

setup(
    name='xtremio',
    version='0.1',
    packages=['xtremio'],
    description="Access XtremIO array using REST API",
    long_description=README,
    install_requires=['requests'],
    author="Scott Howard",
    author_email="scott@doc.net.au",
)
