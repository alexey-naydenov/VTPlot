#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# dualplot.py
#
# Copyright (C) 2013 Alexey Naydenov <alexey.naydenovREMOVETHIS@linux.com>
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

"""Subwindow with a plot and overall plot view."""

import itertools

import PyQt4.QtGui as qtgui
import PyQt4.QtCore as qtcore

import tables
import pyqtgraph as qtgraph

from vitables.plugins.vtplot import plotutils
from vitables.plugins.vtplot import singleplot


class DualPlot(singleplot.SinglePlot):
    def __init__(self, *args, **kwargs):
        super(DualPlot, self).__init__(*args, **kwargs)
        # whether to auto-range only to the visible portion of a plot
        self._plot.setAutoVisible(y=True)
        # zoom functionality
        self._add_overview_plot()
        self._add_zoom_region()
        self._connect_zoom_region_and_plot()
        
    def _add_overview_plot(self):
        self._overview_plot = self._graphics_layout.addPlot(row=1, col=0)
        # setup plot
        for leaf, color in zip(self._leafs, 
                               itertools.cycle(plotutils.PLOT_COLORS)):
            self._overview_plot.plot(leaf, pen=color)
        
    def _add_zoom_region(self):
        self._zoom_region = qtgraph.LinearRegionItem(
            orientation=qtgraph.LinearRegionItem.Vertical)
        self._zoom_region.setZValue(10)
        self._overview_plot.addItem(self._zoom_region, ignoreBounds=True)

    def _connect_zoom_region_and_plot(self):
        self._zoom_region.sigRegionChanged.connect(self._sync_plot_to_region)
        if self._leafs: # plot might be is empty
            data_length = self._leafs[0].shape[0]
            max_len = min(1000, data_length)
            self._zoom_region.setRegion([0, max(max_len, 0.1*data_length)])

    def _sync_plot_to_region(self, unused):
        self._zoom_region.setZValue(10)
        min_x, max_x = self._zoom_region.getRegion()
        # padding = 0 is important because range and plot update each
        # other on change
        self._plot.setXRange(min_x, max_x, padding=0)

    def on_range_changed(self, range_):
        # this handler can be called before _add_zoom_region is called
        if hasattr(self, '_zoom_region'):
            self._zoom_region.setRegion(range_)
