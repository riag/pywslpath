
import io
import re
from setuptools import setup, find_packages

with io.open('src/pywslpath/pywslpath.py', 'rt', encoding='utf-8') as f:
    version = re.search(r'__version__\s*=\s*\'(.*?)\'', f.read()).group(1)

setup(
    name='pywslpath',
    version= version,
    author='riag',
    description='convert WSL Linux to windows path',
    license='Apache',
    author_email='riag@163.com',
    url = 'https://github.com/riag/pywslpath',
    platforms='WSL Linux',
    package_dir={'': 'src'},
    packages = find_packages(
        where='src',
        exclude=['contrib', 'docs', 'tests*', 'tasks']
    ),
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts':[
            'pywslpath=pywslpath.pywslpath:main',
        ]
    },
    zip_safe=False,
)
