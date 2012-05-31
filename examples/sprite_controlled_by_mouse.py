#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

import pygtk
import gtk
import cairo
import gobject

import glucosa



class MainLoop:
    """Representa el bucle principal de un juego.

    Tiene un metodo especial llamado set_controller, en donde
    uno tiene que especificar el objeto que quiere colocar cómo
    administrador del juego.
    """

    def __init__(self, controller, widget, fps=60):
        self.fps = fps
        self._set_controller(controller, widget)

    def _set_controller(self, controller, widget):
        self.controller = controller
        self.widget = widget
        gobject.timeout_add(1000/self.fps, self._update)
        self.widget.connect("expose-event", self._on_draw)

    def _update(self):
        self.controller.on_update()
        gobject.idle_add(self.widget.queue_draw)
        return True

    def _on_draw(self, event, a):
        context = self.widget.window.cairo_create()
        window_size = self.widget.get_window().get_size()
        glucosa.fill(context, (50,50,50), window_size)
        self.controller.on_draw(context)

class Game:
    """Es el administrador del juego.

    Su método ``on_update`` se llamará pedioricamente para mantener
    la velocidad constante del juego. Y el método ``on_draw`` será
    llamado tantas veces como sea posible."""

    def __init__(self):
        self.window = create_window()
        self.mainloop = MainLoop(self, self.window, fps=60)

        image = glucosa.Image('../data/aceituna.png')
        self.sprite = glucosa.Sprite(image, 0, 0)
        self.events = glucosa.Events(self.window)
        self.events.on_mouse_move += self.move_sprite

    def move_sprite(self, event):
        self.sprite.x = event['x']
        self.sprite.y = event['y']

    def on_update(self):
        self.sprite.update()

    def on_draw(self, context):
        self.sprite.draw(context)

if __name__ == '__main__':
    juego = Game()
    gtk.main()
