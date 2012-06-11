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
        self.mainloop = glucosa.MainLoop(self, self.canvas, fps=60)

        image = glucosa.Image('../data/aceituna.png')
        self.sprite = glucosa.Sprite(image, 100, 100, 18, 18, scale=2)
        self.events = glucosa.Events(self.canvas)
        self.events.on_mouse_scroll_up += self.rueda_del_raton_arriba
        self.events.on_mouse_scroll_down += self.rueda_del_raton_abajo

    def rueda_del_raton_arriba(self, evento):
        self.sprite.scale += 0.1

    def rueda_del_raton_abajo(self, evento):
        self.sprite.scale -= 0.1
        if (self.sprite.scale < 1):
            self.sprite.scale = 1

    def on_update(self):
        self.sprite.rotation += 1
        self.sprite.update()

    def on_draw(self, context):
        self.sprite.draw(context)

if __name__ == '__main__':
    juego = Game()
    gtk.main()
