#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# dataplot.py
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

"""QMdiSubWindow adapter to fit vitables application."""

import PyQt4.QtGui as qtgui
import PyQt4.QtCore as qtcore

import vitables.plugin_utils as vtpu

class DataPlot(qtgui.QMdiSubWindow):
    """Adapter for vitables."""
    def __init__(self, parent, index, widget):
        super(DataPlot, self).__init__(parent)
        # store some vars
        self._vtgui = vtpu.getVTGui()
        # window options
        self.setWidget(widget)
        self.setAttribute(qtcore.Qt.WA_DeleteOnClose)
        # stuff that vitables looks for
        self.dbt_leaf = self._vtgui.dbs_tree_model.nodeFromIndex(index)
        self.pindex = qtcore.QPersistentModelIndex(index)
        self.is_context_menu_custom = True
        widget.setParent(self)
