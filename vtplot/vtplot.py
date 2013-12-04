#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# livability.py
#
# Copyright (C) 2013 Alexey Naydenov <alexey.naydenov@linux.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Main plugin class."""

import os
import sys
import functools

import PyQt4.QtGui as qtgui
import PyQt4.QtCore as qtcore

import tables
import pyqtgraph as qtgraph

from vitables import utils as vtutils
from vitables import plugin_utils

from vitables.plugins.vtplot import defaults
from vitables.plugins.vtplot import about_page
from vitables.plugins.vtplot import dataplot

__author__ = defaults.AUTHOR
__version__ = defaults.VERSION
# fields that must be defined: plugin_class, plugin_name, comment
plugin_class = defaults.PLUGIN_CLASS
plugin_name = defaults.PLUGIN_NAME
comment = defaults.COMMENT

def _(s):
    return qtgui.QApplication.translate(defaults.MODULE_NAME, s)

PLOT_COLORS = ['b', 'r', 'g', 'c', 'm', 'y']

def sync_plot_to_region(plot, region, other):
    region.setZValue(10)
    minX, maxX = region.getRegion()
    # padding = 0 is important because range and plot update each other on
    # change
    plot.setXRange(minX, maxX, padding=0)

def sync_region_to_plot(region, window, view_range):
    rgn = view_range[0]
    region.setRegion(rgn)

def move_crosshair(view_box, vertical_line, horizontal_line, event):
    """Move crosshair on mouse event, use with SignalProxy."""
    position = event[0]  # signal proxy turns original arguments into a tuple
    if not view_box.sceneBoundingRect().contains(position):
        return
    mouse_point = view_box.mapSceneToView(position)
    vertical_line.setPos(mouse_point.x())
    horizontal_line.setPos(mouse_point.y())

def add_crosshair_to(plot):
    """Connect mouse move to drawing crosshair on plot."""
    vertical_line = qtgraph.InfiniteLine(angle=90, movable=False)
    horizontal_line = qtgraph.InfiniteLine(angle=0, movable=False)
    plot.addItem(vertical_line, ignoreBounds=True)
    plot.addItem(horizontal_line, ignoreBounds=True)
    proxy = qtgraph.SignalProxy(
        plot.scene().sigMouseMoved, rateLimit=60, 
        slot=functools.partial(move_crosshair, plot.getViewBox(), 
                               vertical_line, horizontal_line))
    plot.crosshair_proxy = proxy # proxy must persist with the plot

def get_data_item_color(data_item):
    return data_item.curve.opts['pen'].color().name()

def get_data_item_value(data_item, position):
    index = int(position + 0.5)
    if index < 0 or index >= len(data_item.yData):
        return 0
    return data_item.yData[index]

LEGEND_LINE = "<span style='color: {color}'>{name} = {value:.3g}</span>"
def update_value_legend(plot_item, label, event):
    """Display data values at x cursor position, use with SignalProxy."""
    position = event[0]  # signal proxy turns original arguments into a tuple
    view_box = plot_item.getViewBox()
    if not view_box.sceneBoundingRect().contains(position):
        return
    mouse_point = view_box.mapSceneToView(position)
    legend = [
        LEGEND_LINE.format(color='black', name='x', value=mouse_point.x()),
        LEGEND_LINE.format(color='black', name='y', value=mouse_point.y())]
    for i, di in enumerate(plot_item.listDataItems()):
        if di.yData is None:
            continue
        legend.append(LEGEND_LINE.format(
            color=get_data_item_color(di), name='y' + str(i+1),
            value=get_data_item_value(di, mouse_point.x())))
    label.setText(' '.join(legend))

def add_legend_with_values_to(plot, label):
    """Show legend with data values under cursor."""
    proxy = qtgraph.SignalProxy(
        plot.scene().sigMouseMoved, rateLimit=60,
        slot=functools.partial(update_value_legend, plot, label))
    plot.data_values_proxy = proxy # proxy must persist with the plot
    
class VTPlot(qtcore.QObject):
    """Main plugin class for all plotting stuff."""

    def __init__(self):
        super(VTPlot, self).__init__()
        
        self._vtgui = plugin_utils.getVTGui()
        self._mdiarea = self._vtgui.workspace
        self._settings = qtcore.QSettings()
        self._logger = plugin_utils.getLogger(defaults.MODULE_NAME)
        self._add_submenu()
        # pyqtgraph options
        qtgraph.setConfigOption('background', 'w')
        qtgraph.setConfigOption('foreground', 'k')

    def helpAbout(self, parent):
        self._about_page = about_page.AboutPage(parent)
        return self._about_page

    def _add_submenu(self):
        """Add submenu with plot actions."""
        actions = [
            qtgui.QAction(_('Dual plot'), self, 
                          triggered=self._plot_large_1d_array,
                          shortcut=qtgui.QKeySequence.UnknownKey,
                          statusTip=_('Plot long array.'))
        ]
        self._submenu = qtgui.QMenu(_(defaults.MENU_NAME))
        for action in actions:
            self._submenu.addAction(action)

        plugin_utils.addToMenuBar(self._submenu)

    def _do_nothing(self):
        """Test plug that logs a message."""
        self._logger.debug('Doing nothing')

    def _set_to_plot_name(self, window):
        """Change window title to current leaf name."""
        window.setWindowTitle(plugin_utils.getSelectedLeaf().name)

    def _is_dimesionality_of_selection(self, dimensions_count):
        """Check if selected object is a leav and has right dimentsionality."""
        current = self._vtgui.dbs_tree_view.currentIndex()
        dbt_leaf = self._vtgui.dbs_tree_model.nodeFromIndex(current)
        if not isinstance(dbt_leaf.node, tables.Leaf):
            self._logger.error(_('Selected object is not an array'))
            return False
        if len(dbt_leaf.node.shape) != dimensions_count:
            self._logger.error(_('Selected object does not have the right '
                                 'number of dimensions'))
            return False
        else:
            return True

    @plugin_utils.long_action(_('Plotting data, please wait ...'))
    def _plot_large_1d_array(self, unused):
        """Plot whole array along with zoomed in version."""
        if not self._is_dimesionality_of_selection(1):
            return
        # create layout and plot
        layout = qtgraph.GraphicsLayoutWidget()
        label = qtgraph.LabelItem(justify='right')
        layout.addItem(label) # row=0, col=0
        zoom_plot = layout.addPlot(row=1, col=0)
        whole_plot = layout.addPlot(row=2, col=0)
        # setup plots
        zoom_plot.setAutoVisible(y=True) # no idea what this does
        add_crosshair_to(zoom_plot)
        add_legend_with_values_to(zoom_plot, label)
        region = qtgraph.LinearRegionItem(
            orientation=qtgraph.LinearRegionItem.Vertical)
        region.setZValue(10) # probably transparency
        # Add the LinearRegionItem to the ViewBox, but tell the
        # ViewBox to exclude this item when doing auto-range
        # calculations.
        whole_plot.addItem(region, ignoreBounds=True)
        # plot data
        leaf = plugin_utils.getSelectedLeaf()
        zoom_plot.plot(leaf, pen=PLOT_COLORS[0])
        whole_plot.plot(leaf, pen=PLOT_COLORS[0])
        # connect signals between zoom_plot and region selection tool
        region.sigRegionChanged.connect(
            functools.partial(sync_plot_to_region, zoom_plot, region))
        zoom_plot.sigRangeChanged.connect(
            functools.partial(sync_region_to_plot, region))
        max_len = min(1000, leaf.shape[0])
        region.setRegion([0, max(max_len, 0.1*leaf.shape[0])])
        # create and show plot window
        index = self._vtgui.dbs_tree_view.currentIndex()
        window = dataplot.DataPlot(self._mdiarea, index, layout)
        self._set_to_plot_name(window)
        self._mdiarea.addSubWindow(window)
        window.show()
