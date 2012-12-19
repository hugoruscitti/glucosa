#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

import gtk
import glucosa

SPEED = 4

class Game:
    """Es el administrador del juego.

    Su método ``on_update`` se llamará pedioricamente para mantener
    la velocidad constante del juego. Y el método ``on_draw`` será
    llamado tantas veces como sea posible."""

    def __init__(self):
        (self.window, self.canvas) = glucosa.create_window()
        self.events = glucosa.Events(self.canvas)
        self.sprites = []
        self._create_keyboard_view()

        self.events.connect('key-pressed', self.on_key_down)
        self.events.connect('key-released', self.on_key_up)

    def _create_keyboard_view(self):
        self.text1 = glucosa.Text("Please, press any key", 20, 40)
        self.text2 = glucosa.Text("", 20, 60)
        self.canvas.add_sprite(self.text1)
        self.canvas.add_sprite(self.text2)

    def on_key_down(self, widget):
        self.text1.text = "You has press: " + ",".join(self.events._keys_pressed)
        #self.update_control_state()

    def on_key_up(self, widget, event):
        self.text2.text = "Last key up: " + event

if __name__ == '__main__':
    juego = Game()
    gtk.main()
