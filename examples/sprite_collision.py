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
        self.canvas.connect('update', self.on_update)
        self.canvas.connect('draw', self.on_draw)

        image = glucosa.Image('../data/aceituna.png')
        self.sprite = glucosa.Sprite(image, 0, 0, 18, 18, type_collision=glucosa.Sprite.COLLISION_CIRCLE)
        self.events = glucosa.Events(self.canvas)
        self.events.connect('mouse-moved', self.move_sprite)

        self.sprite2 = glucosa.Sprite(image, 60, 40, 18, 18, type_collision=glucosa.Sprite.COLLISION_CIRCLE)
        self.texto_colision = glucosa.Text('', 10, 100, face='Arial', size=18,
                                           color = (255, 0, 0))

        self.canvas.add_sprite(self.sprite)
        self.canvas.add_sprite(self.sprite2)

    def move_sprite(self, widget, event):
        self.sprite.set_pos(event['x'], event['y'])

    def on_update(self, area):
        if (self.sprite.collision_with(self.sprite2)):
            self.texto_colision.text = "¡COLISION!"
        else:
            self.texto_colision.text = ""


    def on_draw(self, area, context):
        self.texto_colision.draw(context)

if __name__ == '__main__':
    juego = Game()
    gtk.main()
