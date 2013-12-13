#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# surfplot.py
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

"""Plot 2d data."""

import itertools
import functools as ft

import PyQt4.QtGui as qtgui
import PyQt4.QtCore as qtcore

import numpy as np
import tables
import pyqtgraph as qtgraph
import pyqtgraph.opengl as glgraph

import vitables.plugin_utils as plugin_utils
from vitables.plugins.vtplot import plotutils
from vitables.plugins.vtplot.infoframe import InfoFrame

_MINIMUM_WIDTH = 800 # minimum window width
_MINIMUM_HEIGHT = 600 # minimum window height

class SurfPlot(qtgui.QMdiSubWindow):
    """Adapter for vitables."""

    def __init__(self, parent=None, index=None, leaf=None, leaf_name=None):
        super(SurfPlot, self).__init__(parent)
        self._leaf_name = leaf_name if leaf_name else 'none'
        self._data = leaf
        self._displayed_groups = ['roi']
        # gui stuff
        self.setAttribute(qtcore.Qt.WA_DeleteOnClose)
        self._init_gui()
        # stuff that vitables looks for
        self.dbt_leaf = plugin_utils.getVTGui().dbs_tree_model.nodeFromIndex(index)
        self.pindex = qtcore.QPersistentModelIndex(index)
        self.is_context_menu_custom = True

    def _init_gui(self):
        self.setMinimumWidth(_MINIMUM_WIDTH)
        self.setMinimumHeight(_MINIMUM_HEIGHT)
        self._setup_display_objects()
        self._draw_overview()
        self._setup_splitter()
        # display image
        x_count, y_count = self._data.shape
        scale = x_count/y_count
        #self._overview.setImage(image=np.abs(self._data), autoLevels=True)
        # surf
        scale = 1
        heights = np.abs(self._data)
        heights = scale*heights/np.amax(heights)
        x_count, y_count = heights.shape
        # ensure everything fits into a cube
        xs = np.linspace(-scale, scale, x_count)
        ys = np.linspace(-scale, scale, y_count)
        surf = glgraph.GLSurfacePlotItem(
            x=xs, y=ys, z=heights, shader='heightColor', smooth=False,
            computeNormals=False)
        delta = -0.2
        surf.shader()['colorMap'] = np.array([1/(1 - delta), -delta, 1, 
                                              1/(delta - 1), -1, 1, 
                                              0, 0, 0])
        self._surface.addItem(surf)

    def _setup_display_objects(self):
        self._overview_layout = qtgraph.GraphicsLayoutWidget()
        self._overview_view = self._overview_layout.addViewBox(row=0, col=0)
        self._overview = qtgraph.ImageItem(parent=self._overview_layout)
        self._overview_view.addItem(self._overview)
        self._surface = glgraph.GLViewWidget()
        self._info = InfoFrame(info_groups=self._displayed_groups)

    def _setup_splitter(self):
        self._splitter = qtgui.QSplitter(orientation=qtcore.Qt.Horizontal)
        self._splitter.setStretchFactor(0, 1)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setStretchFactor(2, 0)
        # append objects
        self._splitter.addWidget(self._overview_layout)
        self._splitter.addWidget(self._surface)
        self._splitter.addWidget(self._info)
        self.setWidget(self._splitter)

    def _draw_overview(self):
        self._overview.setImage(image=self._data, autoLevels=True)
