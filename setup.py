#!/usr/bin/env python
# -*- coding: utf-8 -*- #

import setuptools
import setuptools.command.install

<<<<<<< Updated upstream
=======
class BowerCommand(setuptools.Command):
    user_options = []
    """Setuptools command for running ``bower <command>``."""

    description = "Perform bower build."

    def initialize_options(self):
        """Set default values for options."""
        pass

    def finalize_options(self):
        """Finalize options."""
        pass

    def run(self):
        """Execute ``bower`` command."""
        import subprocess
        import sys
        import os
        os.chdir('src/static')
        cmd = ['bower', 'install', '--allow-root']
        errno = subprocess.call(cmd)
        raise SystemExit(errno)


class BuildPyCommand(setuptools.command.install.install):
    """Custom build command."""

    def run(self):
        self.run_command('bower')
        setuptools.command.install.install.run(self)

>>>>>>> Stashed changes

setuptools.setup(name='lvlss',
                 version='0.0.1',
                 description=u'Once upon a time this was a MUDlike.',
                 long_description=open('README.md').read().strip(),
                 author='Derek Arnold',
                 author_email='derek@derekarnold.net',
                 url='http://github.com/lysol/lvlss',
                 packages=setuptools.find_packages(),
                 install_requires=[
                    'flask'
                 ],
                 include_package_data=True,
<<<<<<< Updated upstream
                 license='MIT License'
=======
                 license='MIT License',
                 cmdclass = {
                    'bower': BowerCommand,
                    'install': BuildPyCommand
                    })
>>>>>>> Stashed changes

