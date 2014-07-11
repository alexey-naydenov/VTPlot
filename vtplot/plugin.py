#
# plugin.py
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

"""Main plugin class."""

import logging

import PyQt4.QtGui as qtgui
import PyQt4.QtCore as qtcore

import numpy as np
import tables
import pyqtgraph as qtgraph

from vitables import utils as vtu
from vitables.plugins.aboutpage import AboutPage

import vtplot.defaults as defaults
import vtplot.singleplot as singleplot
import vtplot.dualplot as dualplot
import vtplot.surfplot as surfplot
import vtplot.imageview as imageview
import vtplot.plotutils as plotutils

__author__ = defaults.AUTHOR
__version__ = defaults.VERSION
# fields that must be defined: plugin_class, plugin_name, comment
plugin_class = defaults.PLUGIN_CLASS
plugin_name = defaults.PLUGIN_NAME
comment = defaults.COMMENT


translate = qtcore.QCoreApplication.translate


class VTPlot(qtcore.QObject):
    """Plugin class for interaction with the main program."""

    UID = 'vitables.plugins.vtplot'
    NAME = defaults.PLUGIN_NAME
    COMMENT = defaults.COMMENT

    def __init__(self):
        super(VTPlot, self).__init__()

        self._vtgui = vtu.getGui()
        self._mdiarea = self._vtgui.workspace
        self._settings = qtcore.QSettings()
        self._logger = logging.getLogger(__name__)
        self._add_submenu()
        # pyqtgraph options
        qtgraph.setConfigOption('background', 'w')
        qtgraph.setConfigOption('foreground', 'k')

    def helpAbout(self, parent):
        desc = {'version': defaults.VERSION,
                'module_name': defaults.MODULE_NAME,
                'folder': defaults.FOLDER,
                'author': defaults.AUTHOR,
                'comment': defaults.COMMENT}
        about_page = AboutPage(desc, parent)
        return about_page

    def _add_submenu(self):
        """Add submenu with plot actions."""
        self._plot_actions = [
            qtgui.QAction(translate('vtplot', 'Plot'), self,
                          triggered=self._plot_data,
                          shortcut=qtgui.QKeySequence.UnknownKey,
                          statusTip=translate('vtplot', 'Plot a dataset.')),
        ]
        self._image_actions = [
            qtgui.QAction(translate('vtplot', 'View Image'), self,
                          triggered=self._view_image,
                          shortcut=qtgui.QKeySequence.UnknownKey,
                          statusTip=translate('vtplot', 'Display an image.')),
        ]
        submenu = qtgui.QMenu(defaults.MENU_NAME)
        for action in self._plot_actions:
            submenu.addAction(action)
        for action in self._image_actions:
            submenu.addAction(action)
        # add to menus
        vtu.addToMenuBar(submenu, self._check_selection)
        vtu.addToLeafContextMenu(self._plot_actions,
                                 self._check_selection)
        vtu.addToLeafContextMenu(self._image_actions,
                                 self._check_selection)

    def _check_selection(self):
        """Enable array plots only if all selected objects are 1d arrays."""
        nodes = vtu.getSelectedNodes()
        enabled = plotutils.can_be_plotted(nodes)
        for action in self._plot_actions:
            action.setEnabled(enabled)

    @vtu.long_action(translate('vtplot', 'Plotting data, please wait ...'))
    def _plot_data(self, _):
        """Display 1D or surface plot depending on data dimension."""
        linked_index = vtu.getSelectedIndexes()[0]
        nodes = []
        for node in vtu.getSelectedNodes():
            if node.dtype.kind == 'c':
                node = np.abs(node)
            nodes.append(node)
        if nodes[0].ndim == 1:
            plot_window = dualplot.DualPlot(
                parent=self._mdiarea, index=linked_index, leafs=nodes)
        else:
            leaf_name = vtu.getSelectedNodes()[0]._v_pathname
            plot_window = surfplot.SurfPlot(
                parent=self._mdiarea, index=linked_index,
                leaf=nodes[0], leaf_name=leaf_name)
        self._mdiarea.addSubWindow(plot_window)
        plot_window.show()

    @vtu.long_action(translate('vtplot', 'Plotting data, please wait ...'))
    def _view_image(self, _):
        image_index = vtu.getSelectedIndexes()[0]
        image_window = imageview.ImageView(parent=self._mdiarea,
                                           index=image_index)
        self._mdiarea.addSubWindow(image_window)
        image_window.show()
