
import io
import re
from setuptools import setup, find_packages

with io.open('src/pywslpath/pywslpath.py', 'rt', encoding='utf-8') as f:
    version = re.search(r'__version__\s*=\s*\'(.*?)\'', f.read()).group(1)

setup(
    name='pywslpath',
    version=version,
    author='riag',
    description='Converts Unix and Windows format paths in WSL',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license='Apache',
    author_email='riag@163.com',
    url='https://github.com/riag/pywslpath',
    platforms=['linux',],
    package_dir={'': 'src'},
    packages=find_packages(
        where='src',
        exclude=['contrib', 'docs', 'tests*', 'tasks']
    ),
    install_requires=[
        'click>=7.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'pywslpath=pywslpath.pywslpath:main',
        ]
    },
    zip_safe=False,
)
