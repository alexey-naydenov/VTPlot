VTPlot
======

ViTables data plotting plugin.

## Setting up development environment ##

1. Install `virtualenvwrapper` and create an environment

```sh
mkvirtualenv --python=python3.3 --system-site-packages vtplot
```
or start working in already created environment

```sh
workon vtplot
```

2. Install the following packages from pip if necessary: `numexpr`,
   `cython`, `tables`, `pyqtgraph`.

3. Clone and install `vitables` inside virtual environment.

4. Copy `VTPlot` into `vitables` plugin folder and run it:

```sh
cp -a vtplot ${VIRTUAL_ENV}/lib/python2.7/site-packages/vitables/plugins && ${VIRTUAL_ENV}/bin/vitables  -vvv
```

## TODO ##

* There seems to be a problem with plot object destruction.  Core
  dumps on close sometimes, happens rarely and it is not clear what
  sequence of operations lead to this. It might be caused by functools
  use in signals.
