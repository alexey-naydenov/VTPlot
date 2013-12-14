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
_ROI_MIN_SIZE = 256
_ROI_FRACTION = 0.3

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

    def _setup_display_objects(self):
        self._overview_layout = qtgraph.GraphicsLayoutWidget()
        #self._overview_view = self._overview_layout.addViewBox(row=0, col=0)
        self._overview_view = self._overview_layout.addPlot(row=0, col=0)
        self._overview = qtgraph.ImageItem(parent=self._overview_layout)
        self._overview_view.addItem(self._overview)
        self._surface_view = glgraph.GLViewWidget()
        self._surface = glgraph.GLSurfacePlotItem(
            shader='heightColor', smooth=False, computeNormals=False)
        delta = -0.2
        self._surface.shader()['colorMap'] = np.array(
            [1/(1 - delta), -delta, 1, 
             1/(delta - 1), -1, 1, 
             0, 0, 0])
        self._surface_view.addItem(self._surface)
        self._info = InfoFrame(info_groups=self._displayed_groups)

    def _setup_splitter(self):
        self._splitter = qtgui.QSplitter(orientation=qtcore.Qt.Horizontal)
        self._splitter.setStretchFactor(0, 1)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setStretchFactor(2, 0)
        # append objects
        self._splitter.addWidget(self._overview_layout)
        self._splitter.addWidget(self._surface_view)
        self._splitter.addWidget(self._info)
        self.setWidget(self._splitter)

    def _draw_overview(self):
        self._overview.setImage(image=self._data, autoLevels=True)
        x_count, y_count = self._data.shape
        x_size = max(min(x_count, _ROI_MIN_SIZE), x_count*_ROI_FRACTION)
        y_size = max(min(y_count, _ROI_MIN_SIZE), y_count*_ROI_FRACTION)
        self._overview_roi = qtgraph.RectROI([0, 0], [x_size, y_size], 
                                             pen=(0,9))
        self._overview_roi.addScaleHandle(pos=[0, 0], center=[1, 1])
        self._overview_view.addItem(self._overview_roi)
        self._overview_roi.sigRegionChangeFinished.connect(self._roi_update)
        self._roi_update()

    def _roi_update(self):
        boundaries, transformation = self._overview_roi.getArraySlice(
            self._data, self._overview, returnSlice=False)
        max_x, max_y = self._data.shape
        x_range = (boundaries[0][0], min(max_x - 1, boundaries[0][1]))
        y_range = (boundaries[1][0], min(max_y - 1, boundaries[1][1]))
        self._update_surface(x_range, y_range)

    def _update_surface(self, x_range, y_range):
        data = np.copy(self._data[x_range[0]:x_range[1], y_range[0]:y_range[1]])
        data /= np.amax(data)
        x_data = np.linspace(-1, 1, x_range[1] - x_range[0])
        y_data = np.linspace(-1, 1, y_range[1] - y_range[0])
        self._surface.setData(x=x_data, y=y_data, z=data)

