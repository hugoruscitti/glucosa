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
        self.events = glucosa.Events(self.canvas)
        self.events.on_mouse_move += self.when_move_mouse
        self.lapiz = glucosa.Pencil()

        self.mouse_x = 0
        self.mouse_y = 0

    def when_move_mouse(self, event):
        self.mouse_x = event['x']
        self.mouse_y = event['y']

    def on_update(self):
        pass

    def on_draw(self, context):
        self.lapiz.draw_line(context, 10, 10, 100, 100, 1)
        self.lapiz.draw_circle(context, self.mouse_x, self.mouse_y, 10)
        self.lapiz.draw_arc(context, 100, 120, 60, 0, 180)
        self.lapiz.draw_box(context, 20, 20, 150, 30, 1, (255,0,56))

if __name__ == '__main__':
    juego = Game()
    gtk.main()
