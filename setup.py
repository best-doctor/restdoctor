from typing import Optional

from setuptools import setup, find_packages


def get_version() -> Optional[str]:
    with open('restdoctor/__init__.py', 'r') as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith('__version__'):
            return line.split('=')[-1].strip().strip("'")


def get_long_description() -> str:
    with open('README.md', encoding='utf8') as f:
        return f.read()


setup(
    name='restdoctor',
    description='BestDoctor\'s batteries for REST services.',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    packages=find_packages(),
    include_package_data=True,
    keywords='statistics',
    version=get_version(),
    author='BestDoctor',
    author_email='s.butkin@bestdoctor.ru',
    license='MIT',
    py_modules=['restdoctor'],
    zip_safe=False,
)
