#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

import pygtk
import gtk
import cairo
import gobject
import glucosa



class Game:
    """Es el administrador del juego.

    Su método ``on_update`` se llamará pedioricamente para mantener
    la velocidad constante del juego. Y el método ``on_draw`` será
    llamado tantas veces como sea posible."""

    def __init__(self):
        (self.window, self.canvas) = glucosa.create_window()
        self.canvas.connect('update', self.on_update)
        self.canvas.connect('draw', self.on_draw)

        image = glucosa.Image('../data/aceituna.png')
        self.sprite = glucosa.Sprite(image, 0, 0, 18, 18, scale=2)
        self.events = glucosa.Events(self.canvas)
        self.events.on_mouse_move += self.move_sprite

    def move_sprite(self, event):
        self.sprite.x = event['x']
        self.sprite.y = event['y']

    def on_update(self, area):
        self.sprite.update()

    def on_draw(self, area, context):
        self.sprite.draw(context)

if __name__ == '__main__':
    juego = Game()
    gtk.main()
