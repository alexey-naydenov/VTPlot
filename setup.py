#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='vtplot',
      version='0.1',
      description='ViTables plotting plugin.',
      author='Alexey Naydenov',
      author_email='alexey.naydenov@linux.com',
      packages=find_packages(),
      include_package_data=True,
      requires=['vitables', 'pyqtgraph'],
      entry_points={
          'vitables.plugins': ['vtplot = vtplot.plugin:VTPlot']})
