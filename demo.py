#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

import pygtk
import gtk
import cairo
import gobject

import glucosa


def create_window():
    window = gtk.Window()
    gobject.threads_init()
    window.connect('destroy', gtk.main_quit)
    canvas = gtk.DrawingArea()

    # Añadimos lo eventos que queremos capturar.
    # Esta operación se debe hacer previamente a añadir el DrawingArea a
    # la ventana.
    canvas.set_events(  gtk.gdk.BUTTON_PRESS_MASK
                      | gtk.gdk.BUTTON_RELEASE_MASK
                      | gtk.gdk.KEY_RELEASE_MASK
                      | gtk.gdk.KEY_PRESS_MASK
                      | gtk.gdk.POINTER_MOTION_MASK)

    # Perimitmos que el DrawingArea tenga el foco para pdoer capturar los
    # eventos del teclado.
    canvas.set_flags (gtk.CAN_FOCUS)

    window.add(canvas)
    window.show_all()

    return canvas

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

        self.actores = []

        self.actor_animado = glucosa.Sprite(glucosa.Frame('data/moneda.png', 8), 0, 0)
        self.actor_animado.y = 60
        self.texto = glucosa.Text("Hola Mundo:\n", 5, 150,
                          face="Arial",
                          size=18)

        self.events = glucosa.Events(self.window)
        print self.events.__events__

        self.events.on_mouse_move += self.raton_movido
        self.events.on_mouse_button_pressed += self.boton_mouse_presionado
        self.events.on_key_pressed += self.tecla_pulsada

        self.sound = glucosa.Sound("file:///media/sf_shared/proyectos/glucosa.git/data/jump.wav")
        self.sound.play()

        self.lapiz = glucosa.Pencil()

    def raton_movido(self, evento):
        pass

    def boton_mouse_presionado(self, evento):
        self.crear_actor(evento['x'], evento['y'])

    def tecla_pulsada(self, evento):
        print gtk.gdk.keyval_name(evento['key'])

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
        self.lapiz.draw_box(context, 20, 20, 60, 90, 3)

if __name__ == '__main__':
    juego = Game()
    gtk.main()
