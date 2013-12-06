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

import PyQt4.QtGui as qtgui
import PyQt4.QtCore as qtcore

import tables
import pyqtgraph as qtgraph

import vitables.plugin_utils as plugin_utils
from vitables.plugins.vtplot import plotutils
from vitables.plugins.vtplot.infoframe import InfoFrame

_STATISTICS_WIDTH = 10 # units of fonts symbol 'm'

class SinglePlot(qtgui.QMdiSubWindow):
    """Adapter for vitables."""
    def __init__(self, parent=None, index=None, leafs=None):
        super(SinglePlot, self).__init__(parent)
        # store some vars
        self._vtgui = plugin_utils.getVTGui()
        self._leafs = leafs if leafs else []
        # stuff that vitables looks for
        self.dbt_leaf = self._vtgui.dbs_tree_model.nodeFromIndex(index)
        self.pindex = qtcore.QPersistentModelIndex(index)
        self.is_context_menu_custom = True
        # gui init stuff
        self.setAttribute(qtcore.Qt.WA_DeleteOnClose)
        self._init_gui()

    def _init_gui(self):
        self._splitter = qtgui.QSplitter(parent=self.parent(),
                                         orientation=qtcore.Qt.Horizontal)
        self._plot = qtgraph.PlotWidget(parent=self._splitter, background='w')
        self._info = InfoFrame(parent=self._splitter)
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
