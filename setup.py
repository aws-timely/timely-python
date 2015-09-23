import timely

from setuptools import setup

setup(
    name='timely',
    version=timely.__version__,
    author=timely.__author__,
    author_email='rightlag@gmail.com',
    description='Manage the uptime of Amazon Web Services EC2 containers',
    license='MIT',
    keywords='aws ec2 uptime',
    url='https://github.com/rightlag/timely',
    packages=['timely', 'tests'],
    classifiers=['Development Status :: 4 - Beta']
)
