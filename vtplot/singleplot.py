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
import functools

import PyQt4.QtGui as qtgui
import PyQt4.QtCore as qtcore

import tables
import pyqtgraph as qtgraph

import vitables.plugin_utils as plugin_utils
from vitables.plugins.vtplot import plotutils
from vitables.plugins.vtplot.infoframe import InfoFrame

_MINIMUM_WIDTH = 800 # minimum window width
_MINIMUM_HEIGHT = 600 # minimum window height

_LEGEND_LINE = "<span style='color: {color}'>{name} = {value:.3g}</span>"

def _templates_to_text(template_list, **kwargs):
    return '<br/>'.join([t.format(**kwargs) for t in template_list])

class SinglePlot(qtgui.QMdiSubWindow):
    """Adapter for vitables."""

    _STATISTICS_TEMPLATES = ['min = {min_}', 'max = {max_}', 
                             'mean = {mean}', 'var = {var}']
    _POSITION_INDEX = 0
    _VALUES_INDEX = 1
    _STATISTICS_INDEX = 2

    def __init__(self, parent=None, index=None, leafs=None):
        super(SinglePlot, self).__init__(parent)
        # store some vars
        self._vtgui = plugin_utils.getVTGui()
        self._leafs = leafs if leafs else []
        self._value_names = [l.name for l in self._leafs]
        # stuff that vitables looks for
        self.dbt_leaf = self._vtgui.dbs_tree_model.nodeFromIndex(index)
        self.pindex = qtcore.QPersistentModelIndex(index)
        self.is_context_menu_custom = True
        # gui init stuff
        self.setAttribute(qtcore.Qt.WA_DeleteOnClose)
        self._init_gui()
        # set text edits with some stuff and adjust their size
        self._update_position_info()
        self._update_values_info()
        self._update_statistics_info()
        self._info.fit_content()
        # signal slots
        self._mouse_position_proxy = qtgraph.SignalProxy(
            self._plot.scene().sigMouseMoved, rateLimit=60,
            slot=self._update_position_info)
        self._mouse_value_proxy = qtgraph.SignalProxy(
            self._plot.scene().sigMouseMoved, rateLimit=60,
            slot=self._update_values_info)

    def _init_gui(self):
        """Create gui elements"""
        self.setMinimumWidth(_MINIMUM_WIDTH)
        self.setMinimumHeight(_MINIMUM_HEIGHT)
        self._splitter = qtgui.QSplitter(parent=self.parent(),
                                         orientation=qtcore.Qt.Horizontal)
        self._plot = qtgraph.PlotWidget(parent=self._splitter, background='w')
        self._info = InfoFrame(parent=self._splitter)
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
        self._splitter.addWidget(self._plot)
        self._splitter.addWidget(self._info)
        self.setWidget(self._splitter)

    def _mouse_event_to_coordinates(self, event):
        """Convert proxy event into x, y coordinates."""
        # signal proxy turns original arguments into a tuple
        position = event[0] 
        view_box = self._plot.getViewBox()
        if not view_box.sceneBoundingRect().contains(position):
            return None, None
        mouse_point = view_box.mapSceneToView(position)
        return mouse_point.x(), mouse_point.y()

    def _update_position_info(self, event=None):
        """Update the position text edit on mouse move event.

        Uses signal proxy to reduce number of events.
        """
        if event:
            x, y = self._mouse_event_to_coordinates(event)
            if not x:
                return
        else:
            x, y = 0, 0
        legend = [
            _LEGEND_LINE.format(color='black', name='x', value=x),
            _LEGEND_LINE.format(color='black', name='y', value=y)]
        self._info.update_entry(self._POSITION_INDEX, '<br/>'.join(legend))

    def _update_values_info(self, event=None):
        """Update info text on mouse move event.

        Uses proxy to reduce number of events.
        """
        if event:
            x, y = self._mouse_event_to_coordinates(event)
            if not x:
                return
            values = [plotutils.get_data_item_value(di, x)
                      for di in self._plot.listDataItems()]
        else:
            values = len(self._plot.listDataItems())*[0.0]
        colors = [plotutils.get_data_item_color(di) 
                  for di in self._plot.listDataItems()]
        legend = []
        for value, name, color in zip(values, self._value_names, colors):
            legend.append(_LEGEND_LINE.format(name=name, value=value, 
                                              color=color))
        self._info.update_entry(self._VALUES_INDEX,
                                '<br/>'.join(legend))


    def _update_statistics_info(self, min_=0, max_=0, mean=0, var=0):
        """Update the statistics text edit on the info pane."""
        self._info.update_entry(
            self._STATISTICS_INDEX,
            _templates_to_text(self._STATISTICS_TEMPLATES, min_=0, max_=0,
                               mean=0, var=0))
