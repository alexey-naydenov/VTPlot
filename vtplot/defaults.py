#
# defaults.py
#
# Copyright (C) 2013 Alexey Naydenov <alexey.naydenovREMOVETHIS@gmail.com>
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

"""About page info and names used to register plugin."""

import os.path

AUTHOR = 'Alexey Naydenov <alexey.naydenov@linux.com>'
VERSION = '0.1'
MODULE_NAME = 'vtplot'
PLUGIN_CLASS = 'VTPlot'
PLUGIN_NAME = 'vtplot'
COMMENT = 'Plot 1D and 2D graphs.'
MENU_NAME = 'Plot'

FOLDER = os.path.join(os.path.dirname(__file__))
