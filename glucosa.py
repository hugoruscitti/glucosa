# -*- encoding: utf-8 -*-
import cairo
import os

def fill(context, color, size):
    """Pinta un contexto con un color y tamaño determinado."""
    context.set_source_rgba(*color)
    context.rectangle(0, 0, size[0], size[1])
    context.fill()

def blit_surface(context, surface, x, y, src_x=0, src_y=0, src_width=None, src_height=None):
    """Dibuja una superficie sobre un contexto de canvas."""
    if not src_width:
        src_width = surface.get_width()

    if not src_height:
        src_height = surface.get_height()


    context.set_source_surface(surface, x-src_x, y-src_y)
    context.rectangle(x, y, src_width, src_height)
    context.fill()

def load_surface(path):
    """Genera una superficie a partir de un archivo .png"""

    if not os.path.exists(path):
        raise Exception("File not found: %s" %(path))

    # TODO: no asumir que siempre que cargan PNGs.
    return cairo.ImageSurface.create_from_png(path)

def render_text(context, x, y, text, color, size):
    """Dibuja una cadena de texto sobre el contexto de canvas."""

    context.set_source_rgba(*color)

    context.select_font_face("Monospace",
                cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

    context.set_font_size(size)

    context.move_to(x, y)

    context.show_text(text)

    return context.text_extents(text)[2:4]
