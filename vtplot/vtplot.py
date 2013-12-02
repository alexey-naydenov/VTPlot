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

from PyQt4 import QtGui
from PyQt4 import QtCore

from vitables import utils as vtutils
from vitables import plugin_utils

from vitables.plugins.vtplot import defaults
from vitables.plugins.vtplot import about_page

__author__ = defaults.AUTHOR
__version__ = defaults.VERSION
# fields that must be defined: plugin_class, plugin_name, comment
plugin_class = defaults.PLUGIN_CLASS
plugin_name = defaults.PLUGIN_NAME
comment = defaults.COMMENT

def _(s):
    return QtGui.QApplication.translate(defaults.MODULE_NAME, s)

class VTPlot(QtCore.QObject):
    """Main plugin class for all plotting stuff."""

    def __init__(self):
        super(VTPlot, self).__init__()
        
        self._vtgui = plugin_utils.getVTGui()
        self._settings = QtCore.QSettings()
        self._logger = plugin_utils.getLogger(defaults.MODULE_NAME)

        self._add_submenu()

    def helpAbout(self, parent):
        self._about_page = about_page.AboutPage(parent)
        return self._about_page

    def _add_submenu(self):
        """Add submenu with plot actions."""
        self._submenu = QtGui.QMenu(_(defaults.MENU_NAME))
        actions = {}
        actions['nothing'] = QtGui.QAction(
            _('Nothing'), self, shortcut=QtGui.QKeySequence.UnknownKey,
            triggered=self._do_nothing, statusTip=_('Nothing'))
        self._submenu.addAction(actions['nothing'])

        plugin_utils.addToMenuBar(self._submenu)

        plugin_utils.addToLeafContextMenu(actions.values())

    def _do_nothing(self):
        """Test plug that logs a message."""
        self._logger.debug('Doing nothing')
