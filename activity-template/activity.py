# Copyright 2009 Simon Schampijer
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# This code is based on HelloWorld Activity. Thanks Simon!

"""ActivityTemplate Activity: A case study for developing an activity."""

import gtk
import logging

from gettext import gettext as _

from sugar.activity import activity
from sugar.graphics.toolbarbox import ToolbarBox
from sugar.activity.widgets import ActivityButton
from sugar.activity.widgets import TitleEntry
from sugar.activity.widgets import StopButton
from sugar.activity.widgets import ShareButton
import glucosa

class ActivityTemplate(activity.Activity):
    """ActivityTemplate class as specified in activity.info"""

    def __init__(self, handle):
        """Set up the ActivityTemplate activity."""
        activity.Activity.__init__(self, handle)

        # we do not have collaboration features
        # make the share option insensitive
        self.max_participants = 1

        # toolbar with the new toolbar redesign
        toolbar_box = ToolbarBox()

        activity_button = ActivityButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()

        title_entry = TitleEntry(self)
        toolbar_box.toolbar.insert(title_entry, -1)
        title_entry.show()

        share_button = ShareButton(self)
        toolbar_box.toolbar.insert(share_button, -1)
        share_button.show()

        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

        # Code changes made by glucosa team, the three lines
        # makes the game graphic area.
        canvas = gtk.DrawingArea()
        self.game = Game(canvas)
        self.set_canvas(canvas)

        canvas.show()

class Game:
    """Es el administrador del juego."""

    def __init__(self, canvas):
        self.mainloop = glucosa.MainLoop(self, canvas, fps=30)

        image = glucosa.Image('./aceituna.png')
        self.sprite = glucosa.Sprite(image, 0, 0, 18, 18, scale=1)
        self.sprite.rotation = 40
        self.events = glucosa.Events(canvas)
        self.events.on_mouse_move += self.move_sprite

    def move_sprite(self, event):
        self.sprite.x = event['x']
        self.sprite.y = event['y']

    def on_update(self):
        self.sprite.update()

    def on_draw(self, context):
        self.sprite.draw(context)
