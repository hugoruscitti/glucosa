#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

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
        self.mainloop = glucosa.MainLoop(self, self.canvas, fps=60)

        self.actores = []

        self.actor_animado = glucosa.Sprite(glucosa.Frame('data/moneda.png', 8), 0, 0)
        self.actor_animado.y = 60
        self.texto = glucosa.Text("Hola Mundo:\n", 5, 150,
                          face="Arial",
                          size=18)

        self.events = glucosa.Events(self.canvas)
        print self.events.__events__

        self.events.on_mouse_move += self.raton_movido
        self.events.on_mouse_button_pressed += self.boton_mouse_presionado
        self.events.on_key_pressed += self.tecla_pulsada
        self.events.on_mouse_scroll_up += self.rueda_del_raton_arriba
        self.events.on_mouse_scroll_down += self.rueda_del_raton_abajo

        self.sound = glucosa.Sound("data/jump.wav")
        self.sound.play()

        self.lapiz = glucosa.Pencil()

    def raton_movido(self, evento):
        pass

    def rueda_del_raton_arriba(self, evento):
            print "arriba"


    def rueda_del_raton_abajo(self, evento):
            print "abajo"

    def boton_mouse_presionado(self, evento):
        self.crear_actor(evento['x'], evento['y'])

    def tecla_pulsada(self, evento):
        print self.events.get_keys_pressed()
        if (glucosa.Events.K_RIGHT in self.events.get_keys_pressed()):
            self.actor_animado.x += 2
        if (glucosa.Events.K_LEFT in self.events.get_keys_pressed()):
            self.actor_animado.x -= 2
        if (glucosa.Events.K_UP in self.events.get_keys_pressed()):
            self.actor_animado.y -= 2
        if (glucosa.Events.K_DOWN in self.events.get_keys_pressed()):
            self.actor_animado.y += 2

    def crear_actor(self, x , y):
        self.actores.append(glucosa.Sprite(glucosa.Image('data/aceituna.png'), x, y))

    def on_update(self):
        self.actor_animado.update()

    def on_draw(self, context):
        for actor in self.actores:
            actor.draw(context)

        self.actor_animado.draw(context)
        self.texto.draw(context)
        self.lapiz.draw_line(context, 10, 10, 100, 100, 1)
        self.lapiz.draw_circle(context, 100, 100, 60)
        self.lapiz.draw_arc(context, 100, 120, 60, 0, 180)
        self.lapiz.draw_box(context, 20, 20, 150, 30, 1, (255,0,56))

if __name__ == '__main__':
    juego = Game()
    gtk.main()
