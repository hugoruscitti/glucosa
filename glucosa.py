import cairo
import os

def fill(context, color):
    context.set_source_rgba(*color)
    # TODO: que pinte todo el rectangulo de la ventana.
    context.rectangle(0, 0, 200, 100)
    context.fill()

def blit_surface(context, surface, x, y, src_x=0, src_y=0, src_width=None, src_height=None):
    if not src_width:
        src_width = surface.get_width()

    if not src_height:
        src_height = surface.get_height()

    context.set_source_surface(surface, x, y)
    context.rectangle(x, y, src_width, src_height)
    context.fill()

def load_surface(path):
    if not os.path.exists(path):
        raise Exception("File not found: %s" %(path))

    # TODO: no asumir que siempre que cargan PNGs.
    return cairo.ImageSurface.create_from_png(path)
