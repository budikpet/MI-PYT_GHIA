from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = ''.join(f.readlines())

setup(
    name='ghia_budikpet',
    version='0.3.6',
    description='GHIA CLI and web app tutorial.',
    long_description=long_description,
    keywords="ghia,budikpet, web, cli",
    install_requires=['Flask', 'click>=6', 'requests'],
    author='Petr Budík',
    author_email='budikpet@fit.cvut.cz',
    license='Public Domain',
    url='https://github.com/budikpet/MI-PYT_GHIA',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ghia = ghia.ghia:main',
        ],
    },
    package_data={
        'ghia': ['templates/*.html', 'static/*.css']
        },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries',
        'Framework :: Flask',
        'Environment :: Console',
        'Environment :: Web Environment'
        ],
)