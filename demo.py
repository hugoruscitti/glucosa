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
    window.connect('destroy', gtk.main_quit)
    canvas = gtk.DrawingArea()
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


class Image:
    """Una imagen simple, que puede ser dibujada por un sprite."""

    def __init__(self, path):
        self.surface = glucosa.load_surface(path)

    def blit(self, context, x, y):
        glucosa.blit_surface(context, self.surface, x, y)


class Frame(Image):
    """Representa un cuadro de animación, realizado dividiendo una imagen."""

    def __init__(self, path, cols, rows=1):
        Image.__init__(self, path)
        self.cols = cols
        self.rows = rows
        self.frame_index = 0
        self.frame_limit = cols * rows
        self.frame_width = self.surface.get_width() / self.cols
        self.frame_height = self.surface.get_height() / self.rows
        
        self.frame_coordinates = []
        self.create_frame_coordinates()

    def set_frame(self, index):
        self.frame_index = index

    def blit(self, context, x, y):
        #TODO usar glucosa.blit_surface con parametros para que dibuje
        # solo una parte del tile
        glucosa.blit_surface(context, self.surface, x, y, 
                             self.frame_coordinates[self.frame_index][0], 
                             self.frame_coordinates[self.frame_index][1],
                             self.frame_width, self.frame_height)

    def create_frame_coordinates(self):
        """ Calcula las posiciones del cuadro de animación de la Imagen."""
        
        cont = 0
        while cont <= self.frame_limit:
            frame_col = cont % self.cols
            frame_row = cont / self.cols
            
            dx = frame_col * self.frame_width
            dy = frame_row * self.frame_height
            
            self.frame_coordinates.append([dx, dy])
            
            cont += 1
        
    def advance(self):
        """Avanza un cuadro de animación.

        Este método permite hacer animaciones cíclicas fácilmente. Si
        al momento de avanzar tiene que reiniciar al cuadro 0 lo hace, y
        retorna True avisando del reinicio."""

        self.frame_index += 1

        if self.frame_index >= self.frame_limit:
            self.frame_index = 0
            return True

        return False

class Sprite:
    """Representa a un personaje dentro del juego."""

    def __init__(self, image, x, y):
        self.image = image
        self.x = x
        self.y = y

    def draw(self, context):
        self.image.blit(context, self.x, self.y)

    def update(self):
        if (self.image.__class__.__name__ == "Frame"):
            self.image.advance()

class Text:
    """ Muestra un texto en la pantalla """
    
    def __init__(self, text, x, y, size=12, color=(0,0,0)):
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self, context):
        
        glucosa.render_text(context, self.x, self.y, self.text, 
                            self.color, 
                            self.size)
    
class Game:
    """Es el administrador del juego.

    Su método ``on_update`` se llamará pedioricamente para mantener
    la velocidad constante del juego. Y el método ``on_draw`` será
    llamado tantas veces como sea posible."""

    def __init__(self):
        self.window = create_window()
        self.mainloop = MainLoop(self, self.window, fps=60)
        self.actor = Sprite(Image('../clock-cairo/data/terron.png'), 0, 0)
        self.actor_animado = Sprite(Frame('data/moneda.png', 8), 0, 0)
        self.actor_animado.y = 60
        self.texto = Text("Hola Mundo", 0, 150, 12)

    def on_update(self):        
        self.actor.x += 1
        self.actor_animado.update()

    def on_draw(self, context):
        self.actor.draw(context)
        self.actor_animado.draw(context)
        self.texto.draw(context)

    def on_event(self, event):
        # TODO: como hago para gestionar los eventos (y que gtk los tire) ?
        pass

if __name__ == '__main__':
    juego = Game()
    gtk.main()
