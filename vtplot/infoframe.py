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

import vitables.plugin_utils as plugin_utils
import vitables.plugins.vtplot as vtp
from vitables.plugins.vtplot import defaults

def _(s):
    return qtgui.QApplication.translate(vtp.defaults.MODULE_NAME, s)

_DEFAULT_TEXT_PADDING = 10 # in units of average char width

def set_edits_to_content(edits, text_padding=_DEFAULT_TEXT_PADDING):
    """Change size of text edits to their content.

    All widgets will have the same width equal to the length of
    longest string plus padding. Height is set to number of lines or 1
    if empty.

    """
    if not edits:
        return
    # figure out common wdget width
    text_sizes = [e.fontMetrics().size(0, e.toPlainText()) for e in edits]
    common_width = max([s.width() for s in text_sizes]) \
                   + text_padding*edits[0].fontMetrics().averageCharWidth()
    # set sizes, empty = one line spacing
    for e, s in zip(edits, text_sizes):
        line_spacing = e.fontMetrics().lineSpacing()
        height = s.height() + 1.3*line_spacing # should not have to add this
        e.setFixedSize(qtcore.QSize(common_width, height))

class InfoFrame(qtgui.QFrame):
    """Information frame with cursor position and statistics."""
    DEFAULT_INFO_GROUPS = ['position', 'value', 'min', 'mean', 'max', 'var']
    
    def __init__(self, parent=None, info_groups=None):
        super(InfoFrame, self).__init__(parent)
        info_groups = info_groups if info_groups else self.DEFAULT_INFO_GROUPS
        self._logger = plugin_utils.getLogger(defaults.PLUGIN_NAME)
        # layout and group boxes
        layout = qtgui.QVBoxLayout()
        self._name_display_dict = {}
        self._group_boxes = []
        for group_name in info_groups:
            group_box = qtgui.QGroupBox(parent=self, 
                                        title=_(group_name).capitalize())
            self._group_boxes.append(group_box)
            layout.addWidget(group_box)
            group_layout = qtgui.QVBoxLayout()
            group_box.setLayout(group_layout)
            group_text = qtgui.QTextEdit()
            group_text.setReadOnly(True)
            group_layout.addWidget(group_text)
            group_layout.addStretch()
            self._name_display_dict[group_name] = group_text
        layout.addStretch()
        self.setLayout(layout)

    def update_entry(self, name, text):
        if name not in self._name_display_dict:
            self._logger.error('{0} is not a info element'.format(name))
        self._name_display_dict[name].setHtml(text)

    def fit_content(self):
        set_edits_to_content(self._name_display_dict.values())
        for g in self._group_boxes:
            g.adjustSize()
