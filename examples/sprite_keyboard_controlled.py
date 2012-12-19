#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

import pygtk
import gtk
import cairo
import gobject
import glucosa

SPEED = 4

class State:

    def __init__(self, player):
        self.player = player

    def update(self):
        pass

class StandState(State):

    def __init__(self, player):
        State.__init__(self, player)
        self.player.set_image(self.player.image_stand)

    def update(self):
        if self.player.left_pressed or self.player.right_pressed:
            self.player.set_state(WalkState(self.player))

class WalkState(State):

    def __init__(self, player):
        State.__init__(self, player)
        self.player.set_image(self.player.image_walk)

    def update(self):
        self.player.image.advance(0.25)

        if self.player.left_pressed:
            self.player.x -= SPEED
            self.player.flip = False
        else:
            if self.player.right_pressed:
                self.player.x += SPEED
                self.player.flip = True
            else:
                self.player.set_state(StandState(self.player))

class Player(glucosa.Sprite):

    def __init__(self, events):
        self.image_stand = glucosa.Image("../data/ayni_parado.png")
        self.image_walk = glucosa.Frame("../data/ayni_camina.png", cols=4)
        glucosa.Sprite.__init__(self, self.image_stand, 75, 125, anchor_x=50, anchor_y=100)
        self.set_state(StandState(self))

        # conecta los eventos
        self.events = events
        self.events.connect('key-pressed', self.on_key_down)
        self.events.connect('key-released', self.on_key_up)
        self.left_pressed = False
        self.right_pressed = False

    def set_state(self, state):
        self.state = state

    def on_key_down(self, widget):
        self.update_control_state()

    def on_key_up(self, widget, event):
        self.update_control_state()

    def update_control_state(self):
        self.left_pressed = self.events.is_pressed(glucosa.Events.K_LEFT)
        self.right_pressed = self.events.is_pressed(glucosa.Events.K_RIGHT)
        self.state.update()

class Game:
    """Es el administrador del juego.

    Su método ``on_update`` se llamará pedioricamente para mantener
    la velocidad constante del juego. Y el método ``on_draw`` será
    llamado tantas veces como sea posible."""

    def __init__(self):
        (self.window, self.canvas) = glucosa.create_window()
        self.events = glucosa.Events(self.canvas)
        self.sprites = []
        self._create_player()

    def _create_player(self):
        player = Player(self.events)
        self.canvas.add_sprite(player)


if __name__ == '__main__':
    juego = Game()
    gtk.main()
