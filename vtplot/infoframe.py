#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# infoframe.py
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

"""Information frame with cursor position and statistics."""

import PyQt4.QtGui as qtgui
import PyQt4.QtCore as qtcore

import vitables.plugins.vtplot as vtp

def _(s):
    return qtgui.QApplication.translate(vtp.defaults.MODULE_NAME, s)

class InfoFrame(qtgui.QFrame):
    """Information frame with cursor position and statistics."""
    def __init__(self, parent):
        super(InfoFrame, self).__init__(parent)
        layout = qtgui.QVBoxLayout()
        cursor_box = qtgui.QGroupBox(parent=self, title=_('Position'))
        layout.addWidget(cursor_box)
        value_box = qtgui.QGroupBox(parent=self, title=_('Value'))
        layout.addWidget(value_box)
        self.setLayout(layout)
        
