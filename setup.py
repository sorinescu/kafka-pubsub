#!/usr/bin/env python

import os
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

REQUIREMENTS = [
    'kafka-python>=1.4.4',
    'google-cloud-pubsub'
]

TEST_REQUIREMENTS = [
    'coveralls>=1.5.1',
    'flake8>=2.4.0',
    'pytest>=4.1.1',
    'pytest-cov>=2.6.1'
]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            '--strict',
            '--cov=kafka_pubsub/',
            '--doctest-modules',
            '-vv',
            '--tb=long']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='kafka-pubsub',
    version='0.1',
    description='kafka-pubsub',
    long_description=README,
    author='Sorin Otescu',
    author_email='sorin.otescu@gmail.com',
    url='https://github.com/sorinescu/kafka-pubsub',
    license="MIT",
    install_requires=REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
    keywords=['kafka', 'pubsub', 'google', 'cloud'],
    packages=find_packages(),
    cmdclass={'test': PyTest},
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Topic :: System :: Networking'
    ],
    entry_points={
        'console_scripts': ['demo = demo.demo_handler:main']
    },
)
