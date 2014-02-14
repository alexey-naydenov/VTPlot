#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# vtplot.py
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

import numpy as np
import tables
import pyqtgraph as qtgraph

from vitables import utils as vtutils
from vitables import plugin_utils

import vtplot.defaults as defaults
import vtplot.about_page as about_page
import vtplot.dataplot as dataplot
import vtplot.singleplot as singleplot
import vtplot.dualplot as dualplot
import vtplot.surfplot as surfplot
import vtplot.plotutils as plotutils

__author__ = defaults.AUTHOR
__version__ = defaults.VERSION
# fields that must be defined: plugin_class, plugin_name, comment
plugin_class = defaults.PLUGIN_CLASS
plugin_name = defaults.PLUGIN_NAME
comment = defaults.COMMENT

def _(s):
    return qtgui.QApplication.translate(defaults.MODULE_NAME, s)

class VTPlot(qtcore.QObject):
    """Plugin class for interaction with the main program."""

    UID = 'vitables.plugins.vtplot'
    NAME = defaults.PLUGIN_NAME
    COMMENT = defaults.COMMENT

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
        self._array_actions = [
            qtgui.QAction(_('Plot'), self, 
                          triggered=self._plot_1d_array,
                          shortcut=qtgui.QKeySequence.UnknownKey,
                          statusTip=_('Plot an array.')),
            qtgui.QAction(_('Dual plot'), self, 
                          triggered=self._plot_1d_array_with_zoom,
                          shortcut=qtgui.QKeySequence.UnknownKey,
                          statusTip=_('Plot long array.'))
           
        ]
        self._surf_actions = [
            qtgui.QAction(_('Surf plot'), self,
                          triggered=self._plot_surface,
                          shortcut=qtgui.QKeySequence.UnknownKey,
                          statusTip=_('Plot surface.'))
        ]
        self._submenu = qtgui.QMenu(_(defaults.MENU_NAME))
        for action in self._array_actions + self._surf_actions:
            self._submenu.addAction(action)
        # add to menus
        plugin_utils.addToMenuBar(self._submenu)
        self._submenu.aboutToShow.connect(self._enable_for_right_dimension)
        plotutils.addToLeafContextMenu(self._array_actions, 
                                       self._enable_for_right_dimension)
        plotutils.addToLeafContextMenu(self._surf_actions, 
                                       self._enable_for_right_dimension)
        

    def _enable_for_right_dimension(self):
        """Enable array plots only if all selected objects are 1d arrays."""
        enabled = True
        for leaf in plotutils.getSelectedLeafs():
            if not isinstance(leaf, tables.array.Array) or len(leaf.shape) != 1:
                enabled = False
                break
        for action in self._array_actions:
            action.setEnabled(enabled)
        enabled = True
        for leaf in plotutils.getSelectedLeafs():
            if not isinstance(leaf, tables.array.Array) or len(leaf.shape) != 2:
                enabled = False
                break
        for action in self._surf_actions:
            action.setEnabled(enabled)


    @plugin_utils.long_action(_('Plotting data, please wait ...'))
    def _plot_1d_array_with_zoom(self, unused):
        """Display two plots: overall view and zoomed to region."""
        index = plugin_utils.getVTGui().dbs_tree_view.currentIndex()
        leafs = plotutils.getSelectedLeafs()
        for leaf in leafs:
            if leaf.dtype.kind in 'cSUV':
                self._logger.error(
                    'Can not plot type: {0}'.format(str(leaf.dtype)))
                return
        plot_window = dualplot.DualPlot(parent=self._mdiarea, 
                                        index=index, leafs=leafs)
        self._mdiarea.addSubWindow(plot_window)
        plot_window.show()


    @plugin_utils.long_action(_('Plotting data, please wait ...'))
    def _plot_1d_array(self, unused):
        """Display one plot with crosshair ad statistics."""
        index = plugin_utils.getVTGui().dbs_tree_view.currentIndex()
        leafs = plotutils.getSelectedLeafs()
        for leaf in leafs:
            if leaf.dtype.kind in 'cSUV':
                self._logger.error(
                    'Can not plot type: {0}'.format(str(leaf.dtype)))
                return
        plot_window = singleplot.SinglePlot(parent=self._mdiarea,
                                            index=index, leafs=leafs)
        self._mdiarea.addSubWindow(plot_window)
        plot_window.show()
        
    @plugin_utils.long_action(_('Plotting data, please wait ...'))
    def _plot_surface(self, unused):
        """Display two plots: overall view and zoomed to region."""
        index = plugin_utils.getVTGui().dbs_tree_view.currentIndex()
        leaf = plugin_utils.getSelectedLeaf()
        if leaf.dtype.kind == 'c':
            data = np.abs(leaf)
        else:
            data = np.array(leaf)
        plot_window = surfplot.SurfPlot(parent=self._mdiarea, index=index,
                                        leaf=data, leaf_name=leaf.name)
        self._mdiarea.addSubWindow(plot_window)
        plot_window.show()
