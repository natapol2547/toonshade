# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.utils import register_submodule_factory

bl_info = {
    "name": "Toon Shade",
    "author": "Tawan Sunflower",
    "description": "",
    "blender": (4, 1, 0),
    "version": (0, 0, 1),
    "location": "View3D > Sidebar > Toon Shade",
    "warning": "",
    "category": "Node",
    'support': 'COMMUNITY',
    "tracker_url": "https://github.com/natapol2547/toonshade/issues",
}

from . import auto_load
from . import addon_updater_ops

auto_load.init()

submodules = [
    "panels",
    "properties",
    "operators",
]

_register, _unregister = register_submodule_factory(__name__, submodules)


def register():
    _register()
    addon_updater_ops.register(bl_info.copy())


def unregister():
    addon_updater_ops.unregister()
    _unregister()
