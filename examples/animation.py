#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

import gtk
import gobject

import glucosa


class Game:
    """Es el administrador del juego.

    Su método ``on_update`` se llamará pedioricamente para mantener
    la velocidad constante del juego. Y el método ``on_draw`` será
    llamado tantas veces como sea posible."""

    def __init__(self):
        (self.window, self.canvas) = glucosa.create_window()

        self.canvas.set_update_loop(60)
        self.actores = []

        self.actor_animado = glucosa.Sprite(glucosa.Frame('../data/moneda.png', 8), 0, 0)
        self.canvas.add_sprite(self.actor_animado)
        self.actor_animado.x = 100
        self.actor_animado.y = 60

        self.events = glucosa.Events(self.canvas)

        self.events.connect('key-pressed', self.tecla_pulsada)
	self.events.connect('mouse-button-pressed', self.boton_mouse_presionado)

        self.sound = glucosa.Sound("data/jump.wav")
        self.sound.play()

    def boton_mouse_presionado(self, widget, evento):
        self.crear_actor(evento['x'], evento['y'])

    def tecla_pulsada(self, widget):
        if (self.events.is_pressed(glucosa.Events.K_RIGHT)):
            self.actor_animado.x += 1
        if (self.events.is_pressed(glucosa.Events.K_LEFT)):
            self.actor_animado.x -= 1
        if (self.events.is_pressed(glucosa.Events.K_UP)):
            self.actor_animado.y -= 1
        if (self.events.is_pressed(glucosa.Events.K_DOWN)):
            self.actor_animado.y += 1

    def crear_actor(self, x , y):
        self.actores.append(glucosa.Sprite(glucosa.Image('../data/aceituna.png'), x, y))


if __name__ == '__main__':
    juego = Game()
    gtk.main()
