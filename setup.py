from distutils.core import setup

version = "2.0"
setup(
    name='pankoff',  # How you named your package folder (MyLib)
    packages=['pankoff'],  # Chose the same as "name"
    version=version,  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='Easy fields validator',  # Give a short description about your library
    author='Yaroslav Pankovych',  # Type in your name
    author_email='flower.moor@gmail.com',  # Type in your E-Mail
    url='https://github.com/ypankovych/pankoff',  # Provide either the link to your github or to your website
    download_url=f'https://github.com/ypankovych/pankoff/archive/refs/tags/{version}.tar.gz',  # I explain this later on
    keywords=['validation', 'easy', 'pure python'],  # Keywords that define your package best
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
