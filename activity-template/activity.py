# -*- coding: utf-8 -*-
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
        self.game = Game()
        self.set_canvas(self.game.canvas)

        self.game.canvas.show()

class Game:
    """Es el administrador del juego.

    Su método ``on_update`` se llamará pedioricamente para mantener
    la velocidad constante del juego. Y el método ``on_draw`` será
    llamado tantas veces como sea posible."""

    def __init__(self):
        self.canvas = glucosa.GameArea()
        self.canvas.connect('update', self.on_update)
        self.canvas.set_update_loop(60)

        image = glucosa.Image('../data/aceituna.png')
        self.sprite = glucosa.Sprite(image, 100, 100, 18, 18, scale=2)
        self.canvas.add_sprite(self.sprite)
        self.events = glucosa.Events(self.canvas)
        self.events.connect('mouse-scroll-up', self.rueda_del_raton_arriba)
        self.events.connect('mouse-scroll-down', self.rueda_del_raton_abajo)

    def rueda_del_raton_arriba(self, evento):
        self.sprite.set_scale(0.1)

    def rueda_del_raton_abajo(self, evento):
        self.sprite.set_scale(self.sprite.scale - 0.1)
        if (self.sprite.scale < 1):
            self.sprite.set_scale(1)

    def on_update(self, area):
        self.sprite.rotation += 1
