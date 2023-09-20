from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from distutils.dir_util import copy_tree
import os


class PostDevelopCommand(develop):
    def run(self):
        develop.run(self)
        copy_tree("./examples", os.path.join(os.path.expanduser('~'), ".psearch"))


class PostInstallCommand(install):
    def run(self):
        install.run(self)
        copy_tree("./examples", os.path.join(os.path.expanduser('~'), ".psearch"))


setup(
    name="powershell-search",
    description="tool for searching for patterns in a given path recursively",
    version="0.1.0",

    py_modules=['psearch'],
    entry_points={
        'console_scripts': [
            'psearch=psearch:main',
        ],
    },
    install_requires=[
    ],
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand
    }
)
