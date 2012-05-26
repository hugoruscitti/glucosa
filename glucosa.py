# -*- encoding: utf-8 -*-
import cairo
import os

def fill(context, color, size):
    """Pinta un contexto con un color y tamaño determinado."""
    context.set_source_rgba(*color)
    context.rectangle(0, 0, size[0], size[1])
    context.fill()

def blit_surface(context, surface, x, y, src_x = 0, src_y = 0, src_width = None, src_height = None):
    """Dibuja una superficie sobre un contexto de canvas."""
    if not src_width:
        src_width = surface.get_width()

    if not src_height:
        src_height = surface.get_height()


    context.set_source_surface(surface, x - src_x, y - src_y)
    context.rectangle(x, y, src_width, src_height)
    context.fill()

def load_surface(path):
    """Genera una superficie a partir de un archivo .png"""

    if not os.path.exists(path):
        raise Exception("File not found: %s" % (path))

    # TODO: no asumir que siempre que cargan PNGs.
    return cairo.ImageSurface.create_from_png(path)

def render_text(context, x, y, text, color, size, face):
    """Dibuja una cadena de texto sobre el contexto de canvas."""

    context.set_source_rgba(*color)

    context.select_font_face(face,
                cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

    context.set_font_size(size)

    context.move_to(x, y)

    context.show_text(text)

    return context.text_extents(text)[2:4]

# Sume object oriented stuff

class Image:
    """Una imagen simple, que puede ser dibujada por un sprite."""

    def __init__(self, path):
        self.surface = load_surface(path)

    def blit(self, context, x, y):
        blit_surface(context, self.surface, x, y)

class Frame(Image):
    """Representa un cuadro de animación, realizado dividiendo una imagen."""

    def __init__(self, path, cols, rows = 1):
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
        blit_surface(context, self.surface, x, y,
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
    """Representa a un personaje con apariencia de imagen o animación.

        >>> imagen = glucosa.Image('data/aceituna.png')
        >>> sprite = glucosa.Sprite(imagen, 0, 0)
        >>> sprite.draw(contexto)

    .. image:: ../../data/aceituna.png

    """

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
    """Muestra un texto en la pantalla.

        >>> texto = glucosa.Text('Hola Mundo|nBienvenido a Glucosa!', 10, 100, face='Arial', size=18)
        >>> texto.draw(contexto)

    .. image:: images/texto.png

    """

    def __init__(self, text, x, y, size = 12, color = (0, 0, 0), face = "Monospace"):
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.face = face

    def draw(self, context):

        lines = self.text.split('\n')

        dy = 0

        for line in lines:
            text_width, text_height = render_text(context,
                                                         self.x,
                                                         self.y + dy,
                                                         line,
                                                         self.color,
                                                         self.size,
                                                         self.face)
            dy += text_height


class Singleton(type):
    """ Clase para garantizar que una clase sólo tenga una instancia y
    proporcionar un punto de acceso global a ella.
    """
    def __init__(cls, name, bases, dic):
        super(Singleton, cls).__init__(name, bases, dic)
        cls.instance = None

    def __call__(self, *args, **kw):
        if self.instance is None:
            self.instance = super(Singleton, self).__call__(*args, **kw)
        return self.instance


class _EventsManager:

    # Listado de eventos a capturar.
    __events__ = ('on_mouse_move',
                  'on_mouse_button_pressed',
                  'on_mouse_button_released',
                  'on_key_pressed',
                  'on_key_released' )

    def __getattr__(self, name):
        if hasattr(self.__class__, '__events__'):
            assert name in self.__class__.__events__, \
            "Event '%s' is not declared" % name
        self.__dict__[name] = ev = _EventSlot(name)
        return ev

    def __repr__(self): return 'Events' + str(list(self))

    __str__ = __repr__

    def __len__(self): return NotImplemented

    def __iter__(self):
        def gen(dictitems = self.__dict__.items()):
            for attr, val in dictitems:
                if isinstance(val, _EventSlot):
                    yield val
        return gen()

class _EventSlot:
    """ Evento generico al que se agregan observadores para ser informados
    de cuando se ha producido dicho evento. """

    def __init__(self, name):
        self.targets = []
        self.__name__ = name

    def __repr__(self):
        return 'event ' + self.__name__

    def __call__(self, *a, **kw):
        for f in self.targets: f(*a, **kw)

    def __iadd__(self, f):
        self.targets.append(f)
        return self

    def __isub__(self, f):
        while f in self.targets: self.targets.remove(f)
        return self

class Events(_EventsManager, object):
    """ Gestor de los posibles eventos que se producen en glucosa.

    >>> def boton_mouse_presionado(self, evento):
    >>>     print evento
    >>>
    >>> eventos = glucosa.Events(self.window)
    >>> eventos.on_mouse_button_pressed += self.boton_mouse_presionado

    """

    # Solo puede existir una instancia de este objeto en el programa.
    __metaclass__ = Singleton

    def __init__(self, widget):

        self._widget = widget

        # Conectamos los eventos de GTK.
        self._widget.connect('motion-notify-event',
                             self._mouse_move)
        self._widget.connect('button-press-event',
                             self._mouse_button_press)
        self._widget.connect('button-release-event',
                             self._mouse_button_released)
        self._widget.connect('key-press-event',
                             self._key_pressed)
        self._widget.connect('key-release-event',
                             self._key_released)


    def _mouse_move(self, widget, event):
        mouse_event = {'x' : event.x,
                      'y' : event.y}
        self.on_mouse_move(mouse_event)
        return True

    def _mouse_button_press(self, widget, event):
        print event
        mouse_event = {'button' : event.button,
                      'x' : event.x,
                      'y' : event.y}
        self.on_mouse_button_pressed(mouse_event)
        return True

    def _mouse_button_released(self, widget, event):
        mouse_event = {'button' : event.button,
                      'x' : event.x,
                      'y' : event.y}
        self.on_mouse_button_released(mouse_event)
        return True

    def _key_pressed(self, widget, event):
        key_event = {'key' : event.keyval }
        self.on_key_pressed(key_event)
        return True

    def _key_released(self, widget, event):
        key_event = {'key' : event.keyval }
        self.on_key_released(key_event)
        return True


class Sound:

    def __init__(self, path):
        self.path

    def play(self):
        pass


