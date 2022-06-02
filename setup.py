# coding=utf-8
import re
import ast
from setuptools import setup, find_packages
from os.path import dirname, join, abspath

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('SeleniumRunner/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='SeleniumRunner',
    version=version,
    url='https://github.com/shigebeyond/SeleniumRunner',
    license='BSD',
    author='bugmaster',
    author_email='772910474@qq.com',
    description='SeleniumRunner: make an easy way (yaml) to web automation testing',
    long_description=open(join(abspath(dirname(__file__)), "description.rst"), encoding='utf8').read(),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'PyYAML>=6.0',
        'selenium==4.1.5',
        'selenium-requests==1.4.1',
        'jsonpath>=0.82',
        'lxml==4.3.2',
    ],
    classifiers=[
        'Intended Audience :: Test Engineer',
        'Operating System :: Deepin :: Deepin Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        "Topic :: Software Development :: Testing",
    ],
    entry_points='''
        [console_scripts]
        SeleniumRunner=SeleniumRunner.runner:main
    '''
)
