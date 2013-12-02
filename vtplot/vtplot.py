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
                          triggered=self._plot_large_array,
                          shortcut=qtgui.QKeySequence.UnknownKey,
                          statusTip=_('Plot large array.'))
        ]
        self._submenu = qtgui.QMenu(_(defaults.MENU_NAME))
        for action in actions:
            self._submenu.addAction(action)

        plugin_utils.addToMenuBar(self._submenu)

    def _do_nothing(self):
        """Test plug that logs a message."""
        self._logger.debug('Doing nothing')

    def _plot_large_array(self):
        """One dimensional array plot."""
        # find selected object and check that it is an array
        current_index = self._vtgui.dbs_tree_view.currentIndex()
        dbt_leaf = self._vtgui.dbs_tree_model.nodeFromIndex(current_index)
        if not isinstance(dbt_leaf.node, tables.Array):
            self._logger.error(_('Selected object is not an array'))
            return
        # create graphics objects
        graph_layout = qtgraph.GraphicsLayoutWidget()
        whole_plot = graph_layout.addPlot(row=0, col=0)
        # create mdi window
        plot_window = dataplot.DataPlot(self._mdiarea, current_index, 
                                        graph_layout)
        self._mdiarea.addSubWindow(plot_window)
        plot_window.show()
