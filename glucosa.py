# -*- encoding: utf-8 -*-
import cairo
import os
import gst
import math
import gobject
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

def dec2hex(dec):
    """Devulve la representación de una cadena en hexadecimal de un entero"""
    return "%X" % dec

def hex2dec(hex):
    """Devuelve el valor entero de una cadena en hexadecimal"""
    return int(hex, 16)

def get_pixel_color(x, y, surface):
    """Devuelve el color del pixel solicitado de una surface de cairo."""
    if isinstance(surface, cairo.Surface):
        if surface.get_format() == cairo.FORMAT_ARGB32:
            if surface.get_width() > x >= 0 and surface.get_height() > y >= 0:

                data = surface.get_data()

                bit = surface.get_width() * y * 8 + x * 8

                B = hex2dec(str(data).encode('hex')[bit:bit + 8][0:2])
                G = hex2dec(str(data).encode('hex')[bit:bit + 8][2:4])
                R = hex2dec(str(data).encode('hex')[bit:bit + 8][4:6])
                A = hex2dec(str(data).encode('hex')[bit:bit + 8][6:8])

                return (R, G, B, A)
            else:
                raise Exception("Pixel out of range.")
        else:
            raise Exception("Only RGBA surfaces are accepted.")
    else:
        raise Exception("The surface must be a cairo.Surface.")

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
    canvas = GameArea()

    window.add(canvas)
    window.show_all()

    return (window, canvas)

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


class Sprite(gobject.GObject):
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

    __gsignals__ = {
             'update': (gobject.SIGNAL_RUN_FIRST, None, [])}

    def __init__(self, image, x, y, anchor_x=0, anchor_y=0, scale=1, rotation=0, flip=False):
        gobject.GObject.__init__(self)
        self.image = image
        self.x = x
        self.y = y
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.scale = scale
        self.rotation = rotation
        self.flip = flip
        self.radius = (max(self.image.width, self.image.height) / 2)

    def set_pos(self, x=None, y=None):
        """Define la posicion del personaje"""
        if x:
            self.x = x

        if y:
            self.y = y

    def move(self, mx=0, my=0):
        """Mueve el personaje basandose en la posicion actual
        Ejemplo:
        >>> sprite.move(-10, 0) # Disminuira 10 pixels en x
        >>> sprite.move(0, +10) # Aumentara 10 pixels en y"""
        self.x += mx
        self.y += mx

    def set_anchor(self, x = -1, y = -1):
        """Define el punto de control del personaje"""
        if x >= 0:
            self.anchor_x = x

        if y >= 0:
            self.anchor_y = y
        self.emit('update')

    def set_rotation(self, rotation):
        """Rota el personaje, en grados"""
        self.rotation = rotation
        self.emit('update')

    def set_flip(self, flip):
        """Espejado horizontal"""
        self._flip = flip
        self.emit('update')

    def get_flip(self):
        return self._flip

    flip = property(get_flip, set_flip, doc="Espejado horizontal")

    def set_image(self, image):
        """Define la imagen del sprite"""
        self.image = image
        self.emit('update')

    def set_scale(self, scale):
        """Escalar el sprite"""
        self.scale = scale
        self.emit('update')

    def draw(self, context):
        """ Dibuja un el sprite en el contexto """
        self.image.blit(context, self._x, self._y, scale=self.scale, rotation=self.rotation, anchor_x=self.anchor_x, anchor_y=self.anchor_y, flip=self._flip)

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

    def set_x(self, x):
        self._x = x
        self.emit('update')

    def set_y(self, y):
        self._y = y
        self.emit('update')

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    x = property(get_x, set_x, doc="Define la posicion horizonal")
    y = property(get_y, set_y, doc="Define la posicion vertical")
    
    def get_left(self):
        return self.x - (self.image.width * self.scale / 2)

    def set_left(self, x):
        self.x = x + (self.image.width * self.scale / 2)

    def get_right(self):
        return self.left + (self.image.width * self.scale)

    def set_right(self, x):
        self.set_left(x - self.image.width * self.scale)

    left = property(get_left, set_left, doc="Define la posición izquierda del Sprite")
    right = property(get_right, set_right, doc="Define la posición derecha del Sprite")

    def get_top(self):
        return self.y - (self.image.height * self.scale / 2)

    def set_top(self, y):
        self.y = y + (self.image.height * self.scale / 2)

    def get_bottom(self):
        return self.top + (self.image.height * self.scale)

    def set_bottom(self, y):
        self.set_top(y - self.image.height * self.scale)

    top = property(get_top, set_top, doc="Define la posición superior del Sprite")
    bottom = property(get_bottom, set_bottom, doc="Define la posición inferior del Sprite")
    
    
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


class Events(gobject.GObject):
    """ Gestor de los posibles eventos que se producen en glucosa.

    >>> def boton_mouse_presionado(self, evento):
    >>>     print evento
    >>>
    >>> eventos = glucosa.AreaEvents(self.window)
    >>> eventos.connect('mouse-button-pressed', self.boton_mouse_presionado)


    Los posibles eventos a los que se puede conectar un metodo son:

    - mouse-moved ( al mover el raton por la pantalla ).
    - mouse-button-pressed ( al soltar un botón del ratón ).
    - mouse-button-released ( al presionar un btoón del ratón ).
    - mouse-scroll-up ( al mover la rueda central del raton hacia arriba ).
    - mouse-scroll-down ( al mover la rueda central del raton hacia abajo ).
    - key-pressed ( al pulsar una tecla ).
    - key-released ( al soltar una tecla ).

    """

	# No funciona con gobject:
    # Solo puede existir una instancia de este objeto en el programa.
    #__metaclass__ = Singleton

    __gsignals__ = {'mouse-moved': (gobject.SIGNAL_RUN_FIRST, None, [object]),
					'mouse-button-pressed': (gobject.SIGNAL_RUN_FIRST, None, [object]),
					'mouse-button-released': (gobject.SIGNAL_RUN_FIRST, None, [object]),
					'mouse-scroll-up': (gobject.SIGNAL_RUN_FIRST, None, [object]),
					'mouse-scroll-down': (gobject.SIGNAL_RUN_FIRST, None, [object]),
					'key-pressed': (gobject.SIGNAL_RUN_FIRST, None, []),
					'key-released': (gobject.SIGNAL_RUN_FIRST, None, [])}

    def __init__(self, widget):
        gobject.GObject.__init__(self)

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
        self.emit('mouse-moved', mouse_event)
        return True

    def _mouse_button_press(self, widget, event):
        mouse_event = {'button' : event.button,
                      'x' : event.x,
                      'y' : event.y}
        self.emit('mouse-button-pressed', mouse_event)
        return True

    def _mouse_button_released(self, widget, event):
        mouse_event = {'button' : event.button,
                      'x' : event.x,
                      'y' : event.y}
        self.emit('mouse-button-released', mouse_event)
        return True

    def _mouse_scroll(self, widget, event):
        mouse_event = {'x' : event.x,
                      'y' : event.y}

        if (event.direction == self.scroll_up):
           self.emit('mouse-scroll-up', mouse_event)

        if (event.direction == self.scroll_down):
           self.emit('mouse-scroll-down', mouse_event)

        return True

    def is_pressed(self, key):
        """ Comprueba si una tecla está pulsada

        >>> if (self.events.is_pressed(glucosa.Events.K_b)):
        >>>    print "Ha spulsado la tecla b."
        """
        return (key in self._keys_pressed)

    def _key_repeater(self):
        self.emit('key-pressed')
        return len(self._keys_pressed) > 0

    def _key_pressed(self, widget, event):
        keyvalue = gtk.gdk.keyval_name(event.keyval)

        # Crea una tarea solo si la lista de teclas esta vacia.
        # Cuando se deja de pulsar las teclas la lista se vacia y se
        # puede generar de nuevo una tarea.
        if (len(self._keys_pressed) == 0):
            gobject.timeout_add(10, self._key_repeater)

        self._register_key(keyvalue)
        self.emit('key-pressed')

        return True

    def _key_released(self, widget, event):
        keyvalue = gtk.gdk.keyval_name(event.keyval)
        self._unregister_key(keyvalue)
        self.emit('key-released')
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

class GameArea(gtk.DrawingArea):
    """Es el area donde el juego se dibujará

    Permite ser embebida en cualquier contenedor de gtk, ya que es un
    widget.

    Emite un señal en cada actualizacion y en cada redibujado
    que pueden ser usadas de la siguiente forma:
        >>> area.connect('update', funcion_a_llamar)
        >>> area.connect('draw', funcion_a_llamar)
    """

    __gsignals__ = {
             'update': (gobject.SIGNAL_RUN_FIRST, None, []),
             'draw': (gobject.SIGNAL_RUN_FIRST, None, [object]),
                               }

    def __init__(self):
        gtk.DrawingArea.__init__(self)

        self.sprites = []
        self._timeout = None

        self._background = None
        
        self.connect("expose-event", self._on_draw)

        self.set_events(  gtk.gdk.BUTTON_PRESS_MASK
                          | gtk.gdk.BUTTON_RELEASE_MASK
                          | gtk.gdk.KEY_RELEASE_MASK
                          | gtk.gdk.KEY_PRESS_MASK
                          | gtk.gdk.POINTER_MOTION_MASK)

        self.set_flags (gtk.CAN_FOCUS)

    def add_sprite(self, sprite):
        """Agrega un sprite a el area de juego"""
        self.sprites.append(sprite)
        sprite.connect('update', self._update)
        
    def set_background(self, background):
        """Define el fondo del area de juego"""
        self._background = background
        self.queue_draw()

    def set_update_loop(self, fps=60):
        """Define un bucle de actualizacion si fps = -1 el bucle se detendra
           y dibujara solo cuando un sprite cambie"""
        if self._timeout:
            gobject.source_remove(self._timeout)
        if fps != -1:
            self._timeout = gobject.timeout_add(1000/60, self._update)

    def _update(self, *args):
        # Emite la señal, llamando a todas las funciones que esten conectadas
        # en este caso no pasa argumentos.
        self.emit('update')

        # Se actualizan los sprites
        for sprite in self.sprites:
            sprite.update()

        gobject.idle_add(self.queue_draw)
        return True

    def _on_draw(self, widget, event):
        context = self.window.cairo_create()
        window_size = self.get_window().get_size()
        fill(context, (50,50,50), window_size)

        # Dibuja el fondo
        if self._background:
            self._background.blit(context, 0, 0, scale=1, rotation=0, anchor_x=0,
                                anchor_y=0, flip=False)

        # Se encarga de dibujar los sprites
        for sprite in self.sprites:
            sprite.draw(context)

        # Emite la señal enviando el context como un argumento
        self.emit('draw', context)
