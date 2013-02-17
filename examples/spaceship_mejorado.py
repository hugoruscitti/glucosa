#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

import gtk
import gobject
import random

import glucosa

class Enemy(glucosa.Sprite):

    def __init__(self, game):
        self.game = game
        image = glucosa.Image('../data/aceituna.png')
        x = random.randint(0, 620)
        glucosa.Sprite.__init__(self, image, x, -30, 18, 18, type_collision=glucosa.Sprite.COLLISION_CIRCLE)
        self.speed = random.randint(2, 4)

    def update(self):
        self.y += self.speed

        if self.y > 480:
            self.kill()

    def kill(self):
        self.game.remove_sprite(self)

class Star(glucosa.Sprite):

    def __init__(self):
        image = glucosa.Image('../data/spaceship/starSmall.png')
        x = random.randint(0, 620)
        y = random.randint(0, 480)
        glucosa.Sprite.__init__(self, image, x, y)
        self.speed = random.randint(1, 3)

    def update(self):
        self.y += self.speed

        if self.y > 480:
            self.y = -20
            self.x = random.randint(0, 620)


class Laser(glucosa.Sprite):
    """Representa un disparo de la nave."""

    def __init__(self, game, x, y):
        self.game = game
        image = glucosa.Image('../data/spaceship/laserRed.png')
        glucosa.Sprite.__init__(self, image, x, y, type_collision=glucosa.Sprite.COLLISION_CIRCLE)
        self.game.add_sprite(self)
        self.speed = 20

    def update(self):
        self.y -= self.speed

        if self.y < -50:
            self.kill()

        self._check_collisions()

    def _check_collisions(self):
        for enemy in self.game.enemies:
            if self.collision_with(enemy):
                enemy.kill()
                self.kill()
                return

    def kill(self):
        """Elimina el disparo de la escena."""
        self.game.remove_sprite(self)

class Explosion(glucosa.Sprite):

    def __init__(self, x, y):
        pass

class Ship(glucosa.Sprite):

    def __init__(self, game, x, y):
        self.speed = 6
        self.game = game
        self.can_fire_counter = 1
        self.images = self._load_images()
        self.control = glucosa.Control(self.game.canvas)

        glucosa.Sprite.__init__(self, self.images['player'], x, y)
        self.game.add_sprite(self)

        self.laser_sound = glucosa.Sound("../data/laser.wav")

    def _load_images(self):
        return {
                'player': glucosa.Frame('../data/spaceship/player.png', 1),
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

        if self.can_fire_counter > 0:
            if self.control.fire:
                self.fire()
        else:
            self.can_fire_counter += 1

        self._set_bounds()

    def _set_bounds(self):
        """Se asegura de que la nave no pueda salir de la pantalla"""

        # Bordes horizontales
        if self.x < 0:
            self.x = 0
        elif self.x + 100 > 640:
            self.x = 640 -100

        # Bordes verticales
        if self.y < 0:
            self.y = 0
        elif self.y + 70 > 480:
            self.y = 480 -70


    def fire(self):
        self.laser_sound.stop()
        self.laser_sound.play()
        laser_izquierdo = Laser(self.game, self.x, self.y + 20)
        laser_derecho = Laser(self.game, self.x + 90, self.y + 20)

        # Se asegura de hacer una pausa entre disparos, un
        # valor mas cercano a 0 emite mas disparos por segundo.
        self.can_fire_counter = -5


class Game:
    """Es el administrador del juego.

    Su método ``on_update`` se llamará pedioricamente para mantener
    la velocidad constante del juego. Y el método ``on_draw`` será
    llamado tantas veces como sea posible."""

    def __init__(self):
        (self.window, self.canvas) = glucosa.create_window()
        self.window.resize(640, 480)

        self.canvas.set_update_loop(60)
        self.canvas.set_background(glucosa.Image('../data/space.png'))
        self.ship = Ship(self, 300, 380)

        self.enemies = []
        gobject.timeout_add(1000, self._create_enemy)
        self._create_stars()

    def _create_enemy(self):
        sprite = Enemy(self)
        self.enemies.append(sprite)
        self.canvas.add_sprite(sprite)
        return True

    def add_sprite(self, sprite):
        self.canvas.add_sprite(sprite)

    def remove_sprite(self, sprite):
        self.canvas.remove_sprite(sprite)
        if sprite in self.enemies:
            self.enemies.remove(sprite)

    def _create_stars(self):
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())
        self.add_sprite(Star())

if __name__ == '__main__':
    juego = Game()
    gtk.main()
