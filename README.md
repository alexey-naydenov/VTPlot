VTPlot
======

ViTables data plotting plugin.

## Screenshots ##

![single plot screenshot](docs/images/single_plot.png)

![dual plot screenshot](docs/images/dual_plot.png)

![surf plot screenshot](docs/images/surf_plot.png)


## Setting up development environment ##

1. Install `virtualenvwrapper` and create an environment

```sh
mkvirtualenv --python=python2.7 --system-site-packages vtplot
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
cp -a vtplot ${VIRTUAL_ENV}/lib/python2.7/site-packages/vitables/plugins && ${VIRTUAL_ENV}/bin/vitables -vvv vtplot/test/data/array.h5
```

## TODO ##

* Implement nice plots of data sets with big difference in scale.
* Implement custom horizontal axis values.
* Step plot and events.
* Display selected matrix rows/columns.
* Display multiple graphs below each other.
* Store current settings in a configuration.
* Add settings for displayed statistical information.
* Allow choice between real, imag, abs, angle when plotting complex
  data.
* Plot matrix along with 2 slices.
* Improve surface plot look.
* Add selection between mesh and surface plot.
* Add displaying images along with some image related tools.
* Add plotting for series of images and 3d arrays.
