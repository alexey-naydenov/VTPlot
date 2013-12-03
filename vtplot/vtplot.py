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

def sync_plot_to_region(plot, region):
    region.setZValue(10)
    minX, maxX = region.getRegion()
    # padding is important because range and plot update each other on
    # change
    plot.setXRange(minX, maxX, padding=0)

def sync_region_to_plot(region, window, view_range):
    rgn = view_range[0]
    region.setRegion(rgn)

class VTPlot(qtcore.QObject):
    """Main plugin class for all plotting stuff."""

    def __init__(self):
        super(VTPlot, self).__init__()
        
        self._vtgui = plugin_utils.getVTGui()
        self._mdiarea = self._vtgui.workspace
        self._settings = qtcore.QSettings()
        self._logger = plugin_utils.getLogger(defaults.MODULE_NAME)
        self._add_submenu()
        

    def helpAbout(self, parent):
        self._about_page = about_page.AboutPage(parent)
        return self._about_page

    def _add_submenu(self):
        """Add submenu with plot actions."""
        actions = [
            qtgui.QAction(_('Double plot'), self, 
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
        layout = qtgraph.GraphicsLayoutWidget()
        zoom_plot = layout.addPlot(row=0, col=0)
        whole_plot = layout.addPlot(row=1, col=0)
        leaf = plugin_utils.getSelectedLeaf()
        # setup plots
        zoom_plot.setAutoVisible(y=True)
        region = qtgraph.LinearRegionItem(
            orientation=qtgraph.LinearRegionItem.Vertical)
        region.setZValue(10)
        # Add the LinearRegionItem to the ViewBox, but tell the
        # ViewBox to exclude this item when doing auto-range
        # calculations.
        whole_plot.addItem(region, ignoreBounds=True)
        zoom_plot.plot(leaf)
        whole_plot.plot(leaf)
        region.sigRegionChanged.connect(
            functools.partial(sync_plot_to_region, zoom_plot, region))
        zoom_plot.sigRangeChanged.connect(
            functools.partial(sync_region_to_plot, region))
        region.setRegion([0, max(1000, 0.1*leaf.shape[0])])
        # create and show plot window
        index = self._vtgui.dbs_tree_view.currentIndex()
        window = dataplot.DataPlot(self._mdiarea, index, layout)
        self._set_to_plot_name(window)
        self._mdiarea.addSubWindow(window)
        window.show()
