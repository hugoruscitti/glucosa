#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

import gtk
import math
import glucosa


class Game:
    """Es el administrador del juego.

    Su método ``on_update`` se llamará pedioricamente para mantener
    la velocidad constante del juego. Y el método ``on_draw`` será
    llamado tantas veces como sea posible."""

    def __init__(self):
        (self.window, self.canvas) = glucosa.create_window()
        
        image = glucosa.Image('../data/aceituna.png')
        self.sprite = glucosa.Sprite(image, 100, 100, 18, 18, scale=2)
        self.canvas.add_sprite(self.sprite)
        self.events = glucosa.Events(self.canvas)
        self.events.on_mouse_button_pressed += self.mouse_button_press
        self.events.on_mouse_button_released += self.mouse_button_release
        self.events.on_mouse_move += self.move_sprite
        self._pressed = False

    def mouse_button_press(self, evento):
        self._pressed = True

    def mouse_button_release(self, evento):
        self._pressed = False

    def move_sprite(self, event):
        if self._pressed:
            self.sprite.set_pos(event['x'], event['y'])

if __name__ == '__main__':
    juego = Game()
    gtk.main()
