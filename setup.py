import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-scripts-tracker',
    version='0.2',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='An unofficial Django utility tool that tracks management scripts execution',
    long_description=README,
    url='https://krzysiek555.github.io/django-scripts-tracker/',
    author='Krzysztof Falcman',
    author_email='dev@krzysiekf.cba.pl',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
    ],
)