#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# plotutils.py
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

"""Different utilities and tools for plots."""

import collections

import PyQt4.QtGui as qtgui
import PyQt4.QtCore as qtcore

import numpy as np
import tables
import pyqtgraph as qtgraph

from vitables import utils as vtutils
from vitables import plugin_utils

PLOT_COLORS = ['b', 'r', 'g', 'c', 'm', 'y']
LEGEND_LINE = "<span style='color: {color}'>{name}</span> = {value:.5g}"

def to_list(stuff):
    if stuff is None:
        return []
    if not isinstance(stuff, collections.Iterable):
        return [stuff]
    return stuff

def set_window_title(window, leafs):
    names = [l.name for l in leafs]
    window.setWindowTitle('Plot - ' + ', '.join(names))
    
def add_crosshair_to(plot):
    """Connect mouse move to drawing crosshair on plot."""
    vertical_line = qtgraph.InfiniteLine(angle=90, movable=False)
    horizontal_line = qtgraph.InfiniteLine(angle=0, movable=False)
    plot.addItem(vertical_line, ignoreBounds=True)
    plot.addItem(horizontal_line, ignoreBounds=True)
    # define slot for mouse move
    def move_crosshair(event):
        """Move crosshair on mouse event, use with SignalProxy."""
        position = event[0]  # signal proxy turns original arguments into a tuple
        view_box = plot.getViewBox()
        if not view_box.sceneBoundingRect().contains(position):
            return
        mouse_point = view_box.mapSceneToView(position)
        vertical_line.setPos(mouse_point.x())
        horizontal_line.setPos(mouse_point.y())
    # don't process all mouse moves
    proxy = qtgraph.SignalProxy(plot.scene().sigMouseMoved, rateLimit=60, 
                                slot=move_crosshair)
    return proxy # proxy must persist with the plot

def get_data_item_color(data_item):
    return data_item.curve.opts['pen'].color().name()

def get_data_item_value(data_item, position):
    index = int(position + 0.5)
    if index < 0 or index >= len(data_item.yData):
        return float('nan')
    return data_item.yData[index]

def getDBsTreeView():
    return plugin_utils.getVTGui().dbs_tree_view

def getSelectedIndices():
    return getDBsTreeView().selectionModel().selection().indexes()

def getSelectedLeafs():
    indixes = getSelectedIndices()
    leafs = [plugin_utils.getDBsTreeModel().nodeFromIndex(index).node 
             for index in indixes]
    return leafs

def mouse_event_to_coordinates(plot, event):
    """Convert proxy event into x, y coordinates.

    event is received from signal proxy.
    """
    # signal proxy turns original arguments into a tuple
    position = event[0] 
    view_box = plot.getViewBox()
    if not view_box.sceneBoundingRect().contains(position):
        return None, None
    mouse_point = view_box.mapSceneToView(position)
    return mouse_point.x(), mouse_point.y()

def update_position_info(plot, info_pane, position_name, event=None):
    """Update the position text edit on mouse move event.

    Uses signal proxy to reduce number of events.
    """
    if event:
        x, y = mouse_event_to_coordinates(plot, event)
        if not x:
            return
    else:
        x, y = 0, 0
    legend = [
        LEGEND_LINE.format(color='black', name='x', value=x),
        LEGEND_LINE.format(color='black', name='y', value=y)]
    info_pane.update_entry(position_name, '<br/>'.join(legend))

def calculate_statistics(plot, function, range_):
    stats = []
    for di in plot.listDataItems():
        index_range = np.searchsorted(di.xData, range_)
        if index_range[0] == index_range[1]:
            stats.append(float('nan'))
        else:
            stats.append(function(di.yData[index_range[0]:index_range[1]]))
    return stats
