import os

from codecs import open
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as fp:
    requirements = fp.read().splitlines()

setup(
    name='timely',
    version='0.2.0',
    author='Jason Walsh',
    author_email='rightlag@gmail.com',
    description='Manage the uptime of Amazon Web Services EC2 containers',
    license='MIT',
    keywords='aws ec2 uptime',
    url='https://github.com/rightlag/timely',
    packages=find_packages(exclude=['test*']),
    classifiers=[
        'Development Status :: 4 - Beta',
    ],
    install_requires=requirements
)
