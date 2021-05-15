from distutils.core import setup

version = "6.0"
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
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
