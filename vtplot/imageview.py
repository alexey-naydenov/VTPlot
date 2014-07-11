#
# imageview.py
#
# Copyright (C) 2014 Alexey Naydenov <alexey.naydenovREMOVETHIS@linux.com>
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

"""Mdi window for displaying images."""

import itertools
import functools as ft

import PyQt4.QtGui as qtgui
import PyQt4.QtCore as qtcore

import numpy as np
import pyqtgraph.imageview as iv

from vitables import utils as vtu

from vtplot import plotutils
from vtplot.infoframe import InfoFrame

_MINIMUM_WIDTH = 800 # minimum window width
_MINIMUM_HEIGHT = 600 # minimum window height


class ImageView(qtgui.QMdiSubWindow):
    """Image view mdi window."""

    def __init__(self, parent=None, index=None):
        super(ImageView, self).__init__(parent)
        # fields required by vitables
        self.dbt_leaf = vtu.getModel().nodeFromIndex(index)
        self.pindex = qtcore.QPersistentModelIndex(index)
        self.is_context_menu_custom = True
        # gui init stuff
        self.setAttribute(qtcore.Qt.WA_DeleteOnClose)
        self._init_gui()

    def _init_gui(self):
        """Create gui elements"""
        self.setMinimumWidth(_MINIMUM_WIDTH)
        self.setMinimumHeight(_MINIMUM_HEIGHT)
        view = iv.ImageView(parent=self)
        self.setWidget(view)
