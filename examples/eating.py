#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

import gtk
import gobject
import random

import glucosa


class Fruit(glucosa.Sprite):
    """Representa un disparo de la nave."""

    def __init__(self, game):
        self.game = game
        x = random.randint(0, 640)
        y = random.randint(0, 480)
        image = glucosa.Frame('../data/minifrutas.png', 5, 5)
        image.set_frame(random.randint(0, 5*5))
        glucosa.Sprite.__init__(self, image, x, y, anchor_x=9, anchor_y=9, type_collision=glucosa.Sprite.COLLISION_CIRCLE)
        self.game.add_sprite(self)

    def update(self):
        pass

    def kill(self):
        self.game.remove_sprite(self)


class Effect(glucosa.Sprite):

    def __init__(self, game, x, y):
        self.game = game
        self.image = glucosa.Frame('../data/effecto.png', rows=1, cols=3)
        glucosa.Sprite.__init__(self, self.image, x, y, anchor_x=8, anchor_y=8)
        self.game.add_sprite(self)

    def update(self):
        its_done = self.image.advance(0.1)

        if its_done:
            self.kill()

    def kill(self):
        self.game.remove_sprite(self)

class Player(glucosa.Sprite):

    def __init__(self, game, x, y):
        self.speed = 8
        self.game = game
        self.images = self._load_images()
        self.control = glucosa.Control(self.game.canvas)

        glucosa.Sprite.__init__(self, self.images['player'], x, y,
                anchor_x=19, anchor_y=19, type_collision=glucosa.Sprite.COLLISION_CIRCLE)

        self.game.add_sprite(self)
        self.eat_sound = glucosa.Sound("../data/comer.wav")
        self.contador = 0

    def _load_images(self):
        return {
                'player': glucosa.Frame('../data/aceituna.png', 1),
                'risa': glucosa.Frame('../data/risa.png', 1),
               }

    def update(self):
        if self.control.left:
            self.x -= self.speed
        elif self.control.right:
            self.x += self.speed

        if self.control.down:
            self.y += self.speed
        elif self.control.up:
            self.y -= self.speed

        self._check_collisions()
        self._set_bounds()

        if self.contador > 0:
            self.contador -= 1

            if self.contador == 0:
                self.image = self.images['player']

    def _check_collisions(self):
        for fruit in self.game.fruits:
            if self.collision_with(fruit):
                effect = Effect(self.game, fruit.x, fruit.y)
                fruit.kill()
                self.eat_sound.stop()
                self.eat_sound.play()
                self.scale += 0.1
                self.image = self.images['risa']
                self.contador = 30
                return

    def _set_bounds(self):
        """Se asegura de que el sprite no pueda salir de la pantalla"""

        # Bordes horizontales
        if self.x < 0:
            self.x = 0
        elif self.x + 20 > 640:
            self.x = 640 - 20

        # Bordes verticales
        if self.y < 0:
            self.y = 0
        elif self.y + 40 > 480:
            self.y = 480 - 40

class Game:

    def __init__(self):
        (self.window, self.canvas) = glucosa.create_window()
        self.window.resize(640, 480)

        self.canvas.set_update_loop(60)
        self.canvas.set_background(glucosa.Image('../data/pasto.png'))
        self.player = Player(self, 320, 240)

        # Llama a la funcion _tick una vez por segundo, para
        # crear frutas.
        gobject.timeout_add(1000, self._tick)

        self.fruits = []

    def _tick(self):
        self._create_random_fruit()
        return True

    def _create_random_fruit(self):
        self.fruits.append(Fruit(self))

    def add_sprite(self, sprite):
        self.canvas.add_sprite(sprite)

    def remove_sprite(self, sprite):
        self.canvas.remove_sprite(sprite)
        if sprite in self.fruits:
            self.fruits.remove(sprite)


if __name__ == '__main__':
    juego = Game()
    gtk.main()
