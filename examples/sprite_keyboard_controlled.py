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

class Player(glucosa.Sprite):

    def __init__(self, events):
        self.image_stand = glucosa.Image("../data/ayni_parado.png")
        self.image_walk = glucosa.Frame("../data/ayni_camina.png", cols=4)
        glucosa.Sprite.__init__(self, self.image_stand, 75, 125, anchor_x=50, anchor_y=100)

        self.events = events
        self.events.on_key_pressed += self.on_key_down

    def on_key_down(self):
        if self.events.is_pressed(glucosa.Events.K_LEFT):
            self.x -= SPEED
            self.flip = False
        if self.events.is_pressed(glucosa.Events.K_RIGHT):
            self.x += SPEED
            self.flip = True

class Game:
    """Es el administrador del juego.

    Su método ``on_update`` se llamará pedioricamente para mantener
    la velocidad constante del juego. Y el método ``on_draw`` será
    llamado tantas veces como sea posible."""

    def __init__(self):
        (self.window, self.canvas) = glucosa.create_window()
        self.mainloop = glucosa.MainLoop(self, self.canvas, fps=60)
        self.events = glucosa.Events(self.canvas)
        self.sprites = []
        self._create_player()

    def _create_player(self):
        player = Player(self.events)
        self.sprites.append(player)

    def on_update(self):
        for sprite in self.sprites:
            sprite.update()

    def on_draw(self, context):
        for sprite in self.sprites:
            sprite.draw(context)

if __name__ == '__main__':
    juego = Game()
    gtk.main()
