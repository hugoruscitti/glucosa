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

def blit_surface(context, surface, x, y, src_x=0, src_y=0, src_width=None, src_height=None, scale=1, rotation=0, anchor_x=0, anchor_y=0, flip=False):
    """Dibuja una superficie sobre un contexto de canvas."""
    context.save()

    if not src_width:
        src_width = surface.get_width()

    if not src_height:
        src_height = surface.get_height()

    context.save() # desplazamiento

    context.translate(x-anchor_x, y-anchor_y)


    context.save()
    # mueve el cursor al punto de control
    context.translate(anchor_x, anchor_y)

    if flip:
        context.scale(-1, 1)

    if scale != 1:
        context.scale(scale, scale)

    if rotation:
        context.rotate(math.radians(rotation))

    # restaura el punto de control
    context.translate(-anchor_x, -anchor_y)

    _blit(context, surface, src_x, src_y, src_width, src_height)

    context.restore()
    context.restore()

def _blit(context, surface, src_x, src_y, src_width, src_height):
    "Dibuja una porción de imagen en el contexto del canvas."
    context.set_source_surface(surface, 0-src_x, 0-src_y)
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

    context.save()
    context.set_source_rgba(*color)

    context.select_font_face(face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    context.set_font_size(size)
    context.move_to(x, y)

    context.show_text(text)
    return_value = context.text_extents(text)[2:4]
    context.restore()

    return return_value

def get_absolute_uri(relative_path):
    """Obtiene una ruta uri desde un path relativo.

    Por ejemplo:

        >>> get_absolute_uri("data/my_image.png")
        file:///media/disk/glucosa/data/my_image.png

    """
    absolute_path = os.path.abspath(relative_path)
    return "file://%s" %(absolute_path)

def _range(a, b):
    "Retorna la distancia entre dos numeros."
    return abs(b - a)

def _range_between_two_points((x1, y1), (x2, y2)):
    "Retorna la distancia entre dos puntos en dos dimensiones."
    return math.sqrt(_range(x1, x2) ** 2 + _range(y1, y2) ** 2)


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

    window.add(canvas)
    window.show_all()

    return (window, canvas)

# Sume object oriented stuff

class Image:
    """Una imagen simple, que puede ser dibujada por un sprite.

    Por ejemplo:

        >>> imagen = glucosa.Image('data/fantasma.png')
    """

    def __init__(self, path):
        self.surface = load_surface(path)
        self.width = self.surface.get_width()
        self.height = self.surface.get_height()

    def blit(self, context, x, y, scale=1, rotation=0, anchor_x=0, anchor_y=0, flip=False):
        blit_surface(context, self.surface, x, y,
                              scale=scale, rotation=rotation,
                              anchor_x=anchor_x, anchor_y=anchor_y,
                              flip=flip)

class Frame(Image):
    """Representa un cuadro de animación, realizado dividiendo una imagen.

    Por ejemplo:

        >>> animation = glucosa.Frame("data/player_stand.png", cols=4)
        >>> animation.frame_index
        1
        >>> animation.advance()
        >>> animation.frame_index
        2
        >>> sprite.image = animation

    """

    def __init__(self, path, cols, rows = 1):
        Image.__init__(self, path)
        self.cols = cols
        self.rows = rows
        self.frame_index = 0
        self.frame_limit = cols * rows
        self.frame_width = self.surface.get_width() / self.cols
        self.frame_height = self.surface.get_height() / self.rows

        self.width = self.frame_width
        self.height = self.frame_height

        self.frame_coordinates = []
        self.create_frame_coordinates()

    def set_frame(self, index):
        self.frame_index = index

    def blit(self, context, x, y, scale=1, rotation=0, anchor_x=0, anchor_y=0, flip=False):
        blit_surface(context, self.surface, x, y,
                             self.frame_coordinates[int(self.frame_index)][0],
                             self.frame_coordinates[int(self.frame_index)][1],
                             self.frame_width, self.frame_height,
                             scale=scale, rotation=rotation,
                             anchor_x=anchor_x, anchor_y=anchor_y, flip=flip)

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

    def advance(self, speed=1):
        """Avanza un cuadro de animación.

        Este método permite hacer animaciones cíclicas fácilmente. Si
        al momento de avanzar tiene que reiniciar al cuadro 0 lo hace, y
        retorna True avisando del reinicio."""

        self.frame_index += speed

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
    - flip -- espejado horizontal.
    """

    def __init__(self, image, x, y, anchor_x=0, anchor_y=0, scale=1, rotation=0, flip=False):
        self.image = image
        self.x = x
        self.y = y
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.scale = scale
        self.rotation = rotation
        self.flip = flip
        self.radius = (max(self.image.width, self.image.height) / 2)

    def draw(self, context):
        """ Dibuja un el sprite en el contexto """
        self.image.blit(context, self.x, self.y, scale=self.scale, rotation=self.rotation, anchor_x=self.anchor_x, anchor_y=self.anchor_y, flip=self.flip)

    def update(self):
        """ Actualiza el estado de la animación del Sprite si el Sprite contiene un Frame,
        en vez de una Imagen.
        """
        if (self.image.__class__.__name__ == "Frame"):
            self.image.advance()

    def get_center(self):
        """ Obtiene la posicion central del Sprite """
        return self.x + (self.image.width / 2), self.y + (self.image.height / 2)

    def collision_with(self, sprite):
        "Retorna True si el sprite colisiona con otro sprite."
        return _range_between_two_points(self.get_center(), sprite.get_center()) < self.radius + sprite.radius


class Text:
    """Muestra un texto en la pantalla.

        >>> texto = glucosa.Text('Hola Mundo\\nBienvenido a Glucosa!', 10, 100, face='Arial', size=18)
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

class FPS(Text):

    def __init__(self, mainloop, x, y):
        Text.__init__(self, "FPS: ?", x, y)
        assert isinstance(mainloop, MainLoop)
        self.mainloop = mainloop

    def update(self):
        pass

class Singleton(type):
    """Clase para garantizar que una clase sólo tenga una instancia y
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
                  'on_mouse_scroll_up',
                  'on_mouse_scroll_down',
                  'on_key_pressed',
                  'on_key_released')

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


    Los posibles eventos a los que se puede conectar un metodo son:

    - on_mouse_move ( al mover el raton por la pantalla ).
    - on_mouse_button_pressed ( al soltar un botón del ratón ).
    - on_mouse_button_released ( al presionar un btoón del ratón ).
    - on_mouse_scroll_up ( al mover la rueda central del raton hacia arriba ).
    - on_mouse_scroll_down ( al mover la rueda central del raton hacia abajo ).
    - on_key_pressed ( al pulsar una tecla ).
    - on_key_released ( al soltar una tecla ).

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
        self._widget.connect('scroll-event',
                             self._mouse_scroll)

        self._keys_pressed = []

    def _mouse_move(self, widget, event):
        mouse_event = {'x' : event.x,
                      'y' : event.y}
        self.on_mouse_move(mouse_event)
        return True

    def _mouse_button_press(self, widget, event):
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

    def _mouse_scroll(self, widget, event):
        mouse_event = {'x' : event.x,
                      'y' : event.y}

        if (event.direction == self.scroll_up):
            self.on_mouse_scroll_up(mouse_event)

        if (event.direction == self.scroll_down):
            self.on_mouse_scroll_down(mouse_event)

        return True

    def is_pressed(self, key):
        """ Comprueba si una tecla está pulsada

        >>> if (self.events.is_pressed(glucosa.Events.K_b)):
        >>>    print "Ha spulsado la tecla b."
        """
        return (key in self._keys_pressed)

    def _key_repeater(self):
        self.on_key_pressed()
        return len(self._keys_pressed) > 0

    def _key_pressed(self, widget, event):
        keyvalue = gtk.gdk.keyval_name(event.keyval)

        # Crea una tarea solo si la lista de teclas esta vacia.
        # Cuando se deja de pulsar las teclas la lista se vacia y se
        # puede generar de nuevo una tarea.
        if (len(self._keys_pressed) == 0):
            gobject.timeout_add(10, self._key_repeater)

        self._register_key(keyvalue)
        self.on_key_pressed()

        return True

    def _key_released(self, widget, event):
        keyvalue = gtk.gdk.keyval_name(event.keyval)
        self._unregister_key(keyvalue)
        self.on_key_released()
        return True

    def _register_key(self, key):
        if not(key in self._keys_pressed):
            self._keys_pressed.append(key)

    def _unregister_key(self, key):
        if (key in self._keys_pressed):
            self._keys_pressed.remove(key)

    scroll_up = gtk.gdk.SCROLL_UP
    scroll_down = gtk.gdk.SCROLL_DOWN
    K_a = 'a'
    K_b = 'b'
    K_c = 'c'
    K_d = 'd'
    K_e = 'e'
    K_f = 'f'
    K_g = 'g'
    K_h = 'h'
    K_i = 'i'
    K_j = 'j'
    K_k = 'k'
    K_l = 'l'
    K_m = 'm'
    K_n = 'n'
    #K_ñ = 'ntilde'
    K_o = 'o'
    K_p = 'p'
    K_q = 'q'
    K_r = 'r'
    K_s = 's'
    K_t = 't'
    K_u = 'u'
    K_v = 'v'
    K_w = 'w'
    K_x = 'x'
    K_y = 'y'
    K_z = 'z'
    K_UP = 'Up'
    K_DOWN = 'Down'
    K_LEFT = 'Left'
    K_RIGHT = 'Right'
    K_SPACE = 'space'
    K_RETURN = 'Return'
    K_CONTROL_L = 'Control_L'
    K_CONTROL_R = 'Control_R'
    K_SHIFT_L = 'Shift_L'
    K_SHIFT_R = 'Shift_R'
    K_TAB = 'Tab'


class Sound:
    """Un sonido que se puede reproducir una a mas veces.

        >>> s = Sound("data/sound.wav")
        >>> s.play()
    """

    def __init__(self, path):
        "Genera una nueva instancia de Sound, el parametro ``path`` deber ser ruta al archivo wav."
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

    def draw_circle(self, context, center_x, center_y, radius, line_width=1):
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

class MainLoop:
    """Representa el bucle principal de un juego.

    Tiene un metodo especial llamado set_controller, en donde
    uno tiene que especificar el objeto que quiere colocar cómo
    administrador del juego.
    """

    def __init__(self, controller, widget, fps=60):
        self.fps = fps
        self._set_controller(controller, widget)
        widget.set_events(  gtk.gdk.BUTTON_PRESS_MASK
                          | gtk.gdk.BUTTON_RELEASE_MASK
                          | gtk.gdk.KEY_RELEASE_MASK
                          | gtk.gdk.KEY_PRESS_MASK
                          | gtk.gdk.POINTER_MOTION_MASK)

        widget.set_flags (gtk.CAN_FOCUS)

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
        fill(context, (50,50,50), window_size)
        self.controller.on_draw(context)
