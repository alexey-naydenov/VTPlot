#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# singleplot.py
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

"""Mdi subwindow with single plot with some tools."""

import itertools
import functools as ft

import PyQt4.QtGui as qtgui
import PyQt4.QtCore as qtcore

import numpy as np
import tables
import pyqtgraph as qtgraph

import vitables.plugin_utils as plugin_utils
from vitables.plugins.vtplot import plotutils
from vitables.plugins.vtplot.infoframe import InfoFrame

_MINIMUM_WIDTH = 800 # minimum window width
_MINIMUM_HEIGHT = 600 # minimum window height

_POSITION_GROUP = 'position'
_VALUE_GROUP = 'value'

class SinglePlot(qtgui.QMdiSubWindow):
    """Adapter for vitables."""
    _STAT_FUNCTION_DICT = {'min': np.amin, 'mean': np.mean, 'max': np.amax, 
                           'std': np.std}
    def __init__(self, parent=None, index=None, leafs=None):
        super(SinglePlot, self).__init__(parent)
        # things to display on the right
        self._stat_groups = ['max', 'mean', 'std', 'min']
        self._displayed_groups = [_POSITION_GROUP, _VALUE_GROUP] \
                                 + self._stat_groups
        # store some vars
        self._leafs = leafs if leafs else []
        self._value_names = [l.name for l in self._leafs]
        # stuff that vitables looks for
        self.dbt_leaf = plugin_utils.getVTGui().dbs_tree_model.nodeFromIndex(index)
        self.pindex = qtcore.QPersistentModelIndex(index)
        self.is_context_menu_custom = True
        # gui init stuff
        self.setAttribute(qtcore.Qt.WA_DeleteOnClose)
        self._init_gui()
        # set text edits with some stuff and adjust their size
        plotutils.update_position_info(self._plot, self._info, _POSITION_GROUP)
        self._update_values_info()
        self._update_statistics_info()
        self._info.fit_content()
        # signal slots
        self._mouse_position_proxy = qtgraph.SignalProxy(
            self._plot.scene().sigMouseMoved, rateLimit=30,
            slot=ft.partial(plotutils.update_position_info, self._plot, 
                            self._info, _POSITION_GROUP))
        self._mouse_value_proxy = qtgraph.SignalProxy(
            self._plot.scene().sigMouseMoved, rateLimit=10,
            slot=self._update_values_info)
        self._range_change_proxy = qtgraph.SignalProxy(
            self._plot.sigRangeChanged, rateLimit=10,
            slot=self._update_statistics_info)

    def _init_gui(self):
        """Create gui elements"""
        self.setMinimumWidth(_MINIMUM_WIDTH)
        self.setMinimumHeight(_MINIMUM_HEIGHT)
        self._splitter = qtgui.QSplitter(parent=self.parent(),
                                         orientation=qtcore.Qt.Horizontal)
        self._graphics_layout = qtgraph.GraphicsLayoutWidget()
        self._plot = self._graphics_layout.addPlot(row=0, col=0)
        self._info = InfoFrame(parent=self._splitter, 
                               info_groups=self._displayed_groups)
        # only stretch plot window
        self._splitter.setStretchFactor(0, 1)
        self._splitter.setStretchFactor(1, 0)
        # setup plot
        for leaf, color in zip(self._leafs, 
                               itertools.cycle(plotutils.PLOT_COLORS)):
            self._plot.plot(leaf, pen=color)
        plotutils.set_window_title(self, self._leafs)
        # signals and slots
        self._cross_proxy = plotutils.add_crosshair_to(self._plot)
        # combine objects
        self._splitter.addWidget(self._graphics_layout)
        self._splitter.addWidget(self._info)
        self.setWidget(self._splitter)

    def _update_info(self, info_name, values):
        colors = [plotutils.get_data_item_color(di) 
                  for di in self._plot.listDataItems()]
        legend = []
        for value, name, color in zip(values, self._value_names, colors):
            legend.append(plotutils.LEGEND_LINE.format(name=name, value=value, 
                                              color=color))
        self._info.update_entry(info_name, '<br/>'.join(legend))

    def _update_values_info(self, event=None):
        """Update info text on mouse move event.

        Uses proxy to reduce number of events.
        """
        if event:
            x, y = plotutils.mouse_event_to_coordinates(self._plot, event)
            if not x:
                return
            values = [plotutils.get_data_item_value(di, x)
                      for di in self._plot.listDataItems()]
        else:
            values = len(self._plot.listDataItems())*[float('nan')]
        self._update_info(_VALUE_GROUP, values)


    def _update_statistics_info(self, unused=None):
        """Update the statistics text edit on the info pane."""
        x_range = self._plot.viewRange()[0]
        for stat_name in self._stat_groups:
            stat_values = plotutils.calculate_statistics(
                plot=self._plot, function=self._STAT_FUNCTION_DICT[stat_name],
                range_=x_range)
            self._update_info(stat_name, stat_values)
        self.on_range_changed(x_range)

    def on_range_changed(self, range_):
        """Place holder for child to redefine."""
        pass

