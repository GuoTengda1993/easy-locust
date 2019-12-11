# -*- coding: utf-8 -*-
import ast
import os
import re

from setuptools import find_packages, setup


# parse version from locust/__init__.py
_version_re = re.compile(r'__version__\s+=\s+(.*)')
_init_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "easy_locust", "__init__.py")
with open(_init_file, 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='easy-locust',
    version=version,
    description="Extensions for locustio",
    long_description=open("README.md", encoding='utf-8').read(),
    classifiers=[
        "Topic :: Software Development :: Testing :: Traffic Generation",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
    ],
    keywords='',
    author='Guo Tengda',
    author_email='ttguotengda@foxmail.com',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=["locustio>=0.13.0", "paramiko>=2.4.1", "xlrd>=1.2.0"],
    # test_suite="",
    # tests_require=['mock'],
    entry_points={
        'console_scripts': [
            'easy-locust = easy_locust.main:main',
        ]
    },
)
