from setuptools import setup, find_packages

from codecs import open
from os import path
import re

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

"""py_modules=["master-transcoder.a","slave-transcoder"],"""
setup(
    name='phwrt',
    version='1.0',
    description='Plex Remote Hardware Transcoder',
    long_description=long_description,
    url='',
    author='thomas goureau',
    author_email='thomas.goureau@github',
    license='',
	test_suite = 'tests',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='plex remote hw transcoding',
	py_modules=["master_transcoder","slave_transcoder","utilsphwrt"],
    entry_points={
        'console_scripts': [
            'phwrt-master=master_transcoder:main',
            'phwrt-m-tr=master_transcoder:subtring_optimisation',
            'phwrt-slave=slave_transcoder:main'
        ],
    },
    #install_requires=['termcolor', 'psutil']
)