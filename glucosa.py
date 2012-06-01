# -*- encoding: utf-8 -*-
import cairo
import os
import pygst
pygst.require("0.10")
import gst, gtk
import math
import gobject
import pygtk
import gtk

def fill(context, color, size):
    """Pinta un contexto con un color y tamaño determinado."""
    context.set_source_rgba(*color)
    context.rectangle(0, 0, size[0], size[1])
    context.fill()

def blit_surface(context, surface, x, y, src_x=0, src_y=0, src_width=None, src_height=None, scale=1, rotation=0):
    """Dibuja una superficie sobre un contexto de canvas."""
    if not src_width:
        src_width = surface.get_width()

    if not src_height:
        src_height = surface.get_height()

    context.translate(x, y)

    if scale != 1:
        context.scale(scale, scale)

    if rotation:
        context.rotate(math.radians(rotation))

    context.set_source_surface(surface, - src_x, - src_y)
    context.rectangle(0, 0, src_width, src_height)
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

def get_absolute_uri(relative_path):
    """Creates a uri string from a relative path.

    Example:

        >>> get_absolute_uri("data/my_image.png")
        file:///media/disk/glucosa/data/my_image.png

    """
    absolute_path = os.path.abspath(relative_path)
    return "file://%s" %(absolute_path)

def create_window():
    """Genera una ventana con un elemento DrawingArea dentro.

    Esta función se utiliza para simplificar pruebas rápidas y
    la construcción de ejemplos sencillos. No es una función muy
    sofisticada, solo es un helper.

    El objeto retornado por esta función es una tupla con dos
    elementos, la ventana creada y el DrawingArea.
    """
    window = gtk.Window()
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

    # Perimitmos que el DrawingArea tenga el foco para poder capturar los
    # eventos del teclado.
    canvas.set_flags (gtk.CAN_FOCUS)

    window.add(canvas)
    window.show_all()

    return (window, canvas)

# Sume object oriented stuff

class Image:
    """Una imagen simple, que puede ser dibujada por un sprite."""

    def __init__(self, path):
        self.surface = load_surface(path)

    def blit(self, context, x, y, scale=1, rotation=0):
        blit_surface(context, self.surface, x, y, scale=scale, rotation=rotation)

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

    def blit(self, context, x, y, scale=1, rotation=0):
        #TODO usar glucosa.blit_surface con parametros para que dibuje
        # solo una parte del tile
        blit_surface(context, self.surface, x, y,
                             self.frame_coordinates[self.frame_index][0],
                             self.frame_coordinates[self.frame_index][1],
                             self.frame_width, self.frame_height,
                             scale=scale, rotation=rotation)

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

    Cada Sprite tiene atributos para representar el estado de dibujado, alguno
    de estos atributos son:

    - x -- posición horizontal.
    - y -- posición vertical.
    - anchor_x -- punto de control horizontal.
    - anchor_y -- punto de control vertical.
    - scale -- tamaño del sprite (por ejemplo: 1 es normal, 2 el doble de tamaño...)
    - rotation -- la rotación en grados.
    """

    def __init__(self, image, x, y, anchor_x=0, anchor_y=0, scale=1, rotation=0):
        self.image = image
        self.x = x
        self.y = y
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.scale = scale
        self.rotation = rotation

    def draw(self, context):
        self.image.blit(context, self.x - self.anchor_x, self.y - self.anchor_y, scale=self.scale, rotation=self.rotation)

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

    Para que una clase sea Singleton simplemente se tiene que
    cambiar la metaclase por Singleton. Por ejemplo::

        class MiClase:
            __metaclass__ = Singleton
            [...]

    Entonces, la clase tendrá una sola instancia activa:

        >>> a = MiClase()
        >>> b = MiClase()
        >>> id(a) == id(b)
        True
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
    """Un sonido que se puede reproducir una a mas veces.

        >>> s = Sound("file://data/sound.wav")
        >>> s.play()
    """

    def __init__(self, path):
        "Creates a new sound instance, ``path`` must be a string with route to wav file."
        self.path = path
        self.player = gst.element_factory_make("playbin2", "player")
        self.player.set_property("uri", get_absolute_uri(path))

        self.bus = self.player.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_message)

    def play(self):
        "Reproduce el sonido."
        self.player.set_state(gst.STATE_PLAYING)

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.playmode = False
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.playmode = False

class Pencil:
    """Representa un contexto de dibujo donde se pueden dibujar figuras geometricas.

        >>> self.lapiz = glucosa.Pencil()
        >>> self.lapiz.draw_line(context, 10, 10, 100, 100, 1)
    """


    def __init__(self, color=(0, 0, 0)):
        self.color = color

    def draw_line(self, context, src_x, src_y, dest_x, dest_y, line_width=1):
        """ Dibuja una linea recta en pantalla.

        >>> self.lapiz = glucosa.Pencil()
        >>> self.lapiz.draw_line(context, 10, 10, 100, 100, 1)

        """

        context.set_source_rgba(*self.color)

        context.move_to(src_x, src_y)
        context.line_to(dest_x, dest_y)

        context.set_line_width(line_width)

        context.stroke()

    def draw_circle (self, context, center_x, center_y, radius, line_width=1):
        """ Dibuja un circulo en pantalla

        >>> self.lapiz = glucosa.Pencil()
        >>> self.lapiz.draw_circle(context, 100, 100, 60)

        """
        self.draw_arc(context, center_x, center_y, radius, 0, 360, line_width)

    def draw_arc(self, context, center_x, center_y, radius, angle_1, angle_2,
                 line_width=1):
        """ Dibuja un arco en pantalla. Los angulos crecen en el sentido de
        las agujas del reloj.

        >>> self.lapiz = glucosa.Pencil()
        >>> self.lapiz.draw_arc(context, 100, 120, 60, 0, 180)

        """

        context.set_source_rgba(*self.color)

        context.set_line_width(line_width)

        context.arc(center_x, center_y, radius, angle_1 * (math.pi / 180),
                    angle_2 * (math.pi / 180))

        context.stroke()

    def draw_box (self, context, x, y, width, height, line_width=1,
                  fill_color=None):
        """ Dibuja una caja en pantalla. """

        context.set_source_rgba(*self.color)

        context.set_line_width(line_width)

        context.move_to(x, y)
        context.line_to(x + width, y)
        context.line_to(x + width, y + height)
        context.line_to(x, y + height)

        context.close_path()

        if (fill_color != None):
            context.set_source_rgba(*fill_color)
            context.fill_preserve()
            context.set_source_rgba(*self.color)

        context.stroke()
