#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# about_page.py
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

"""VTPlot plugin about page."""

import os

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic

from vtplot import defaults

def _(s):
    return QtGui.QApplication.translate(defaults.MODULE_NAME, s)

Ui_AboutPage = uic.loadUiType(os.path.join(defaults.FOLDER,
                                           'ui/about_page.ui'))[0]

class AboutPage(QtGui.QWidget, Ui_AboutPage):
    def __init__(self, parent=None):
        super(AboutPage, self).__init__(parent)
        self.setupUi(self)
        # fill gui elements
        self.version_text.setText(defaults.VERSION)
        self.module_name_text.setText(defaults.MODULE_NAME)
        self.folder_text.setText(defaults.FOLDER)
        self.author_text.setText(defaults.AUTHOR)
        self.desc_text.setText(defaults.COMMENT)

                                                         
        
