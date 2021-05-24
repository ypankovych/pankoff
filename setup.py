"""
See documentation at https://pankoff.rtfd.io/
"""
from distutils.core import setup

version = "15.4"
setup(
    name='pankoff',
    packages=['pankoff'],
    version=version,
    license='MIT',
    description='Easy fields validator',
    author='Yaroslav Pankovych',
    author_email='flower.moor@gmail.com',
    url='https://github.com/ypankovych/pankoff',
    download_url=f'https://github.com/ypankovych/pankoff/archive/refs/tags/{version}.tar.gz',
    keywords=['validation', 'easy', 'pure python'],
    long_description=__doc__,
    classifiers=[
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython'
    ],
)
