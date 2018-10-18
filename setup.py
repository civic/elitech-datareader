from setuptools import setup,find_packages
import os

from os import path
import io

this_directory = path.abspath(path.dirname(__file__))
with io.open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
setup(
    name='elitech-datareader',
    version='1.0.3',
    packages=find_packages(),
    url='http://github.com/civic/elitech-datareader/',
    license='MIT',
    author='civic',
    author_email='dev@civic-apps.com',
    description='Elitech rc4 data access tool and library.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms='any',
    test_suite = "tests",
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points="""
    [console_scripts]
    elitech-datareader=scripts.elitech_device:main
    """,
    dependency_links=["http://www.silabs.com/products/mcu/Pages/USBtoUARTBridgeVCPDrivers.aspx"]

)
