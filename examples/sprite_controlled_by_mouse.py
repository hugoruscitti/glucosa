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

        image = glucosa.Image('../data/aceituna.png')
        self.sprite = glucosa.Sprite(image, 0, 0, 18, 18, scale=2)
        self.canvas.add_sprite(self.sprite)
        self.events = glucosa.Events(self.canvas)
        self.events.on_mouse_move += self.move_sprite

    def move_sprite(self, event):
        self.sprite.set_pos(event['x'], event['y'])


if __name__ == '__main__':
    juego = Game()
    gtk.main()
