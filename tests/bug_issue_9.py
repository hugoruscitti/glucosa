#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

import glucosa


(window, canvas) = glucosa.create_window()
image = glucosa.Image('../data/aceituna.png')
sprite = glucosa.Sprite(image, 0, 0, 18, 18, type_collision=glucosa.Sprite.COLLISION_CIRCLE)

arriba = sprite.get_top()
abajo = sprite.get_bottom()

sprite.set_top(arriba - 100)

assert sprite.get_top() == arriba - 100
assert sprite.get_bottom() == abajo - 100

sprite.left = 0
assert sprite.right == 37

sprite.left = -100
assert sprite.right == -100 + 37
