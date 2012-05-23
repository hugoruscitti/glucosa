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

    def __init__(self, path, cols, rows=1):
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

    def __init__(self, text, x, y, size=12, color=(0,0,0), face="Monospace"):
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
    def __init__(cls, name, bases, dic):
        super(Singleton, cls).__init__(name, bases, dic)
        cls.instance = None

    def __call__(self, *args, **kw):
        if self.instance is None:
            self.instance = super(Singleton, self).__call__(*args, **kw)
        return self.instance            

# Creamos las constantes de los posibles eventos.
EVENT_MOUSE_MOVE = "motion-notify-event"
EVENT_MOUSE_BUTTON_PRESSED = "button-press-event"
EVENT_MOUSE_BUTTON_RELEASED = "button-release-event"
EVENT_KEY_PRESSED = "key-press-event"
EVENT_KEY_RELEASED = "key-release-event"

class Events(object):
    
    __metaclass__ = Singleton
    
    def __init__(self, widget):
        
        self._event_manager = _EventManager()
        self._event_manager.add_event(_Event(EVENT_MOUSE_MOVE))
        self._event_manager.add_event(_Event(EVENT_MOUSE_BUTTON_PRESSED))
        self._event_manager.add_event(_Event(EVENT_MOUSE_BUTTON_RELEASED))
        self._event_manager.add_event(_Event(EVENT_KEY_PRESSED))
        self._event_manager.add_event(_Event(EVENT_KEY_RELEASED))

        
        self._widget = widget
        self._widget.connect(EVENT_MOUSE_MOVE, 
                             self._mouse_move)
        self._widget.connect(EVENT_MOUSE_BUTTON_PRESSED, 
                             self._mouse_button_press)
        self._widget.connect(EVENT_MOUSE_BUTTON_RELEASED, 
                             self._mouse_button_released)
        self._widget.connect(EVENT_KEY_PRESSED, 
                             self._key_pressed)
        self._widget.connect(EVENT_KEY_RELEASED, 
                             self._key_released)
   
    def _mouse_move(self, widget, event):
        
        mouse_event = {'event' : {'button' : event.button,
                      'x' : event.x,
                      'y' : event.y}
                      }
        
        self._event_manager.signal(EVENT_MOUSE_MOVE, mouse_event)
        
        return True
    
    def _mouse_button_press(self, widget, event):
        
        mouse_event = {'event' : {'button' : event.button,
                      'x' : event.x,
                      'y' : event.y}
                      }
        
        self._event_manager.signal(EVENT_MOUSE_BUTTON_PRESSED, mouse_event)
        
        return True
    
    def _mouse_button_released(self, widget, event):
        
        mouse_event = {'event' : {'button' : event.button,
                      'x' : event.x,
                      'y' : event.y}
                      }
        
        self._event_manager.signal(EVENT_MOUSE_BUTTON_RELEASED, mouse_event)
        
        return True
    
    def _key_pressed(self, widget, event):
        key_event = {'event' : {'key' : event.keyval }}
        
        self._event_manager.signal(EVENT_KEY_PRESSED, key_event)
        
        return True
    
    def _key_released(self, widget, event):
        key_event = {'event' : {'key' : event.keyval }}
        
        self._event_manager.signal(EVENT_KEY_RELEASED, key_event)
        
        return True
    
        
    def connect(self, event, function):
        self._event_manager.connect(event, function)

class _Event():
    def __init__(self, name):
        self.name = name
        self.listeners = {}

    def add(self, function, data=None):
        self.listeners[function] = data
    
    def delete(self, function):
        self.listeners.pop(function)

    def called(self, data=None):
        for function, d in self.listeners.items():
            if data is None:
                if d is None:
                    function()
                else:
                    if type(d) == type([]):
                        function(*d)
                    elif type(d) == type({}):
                        function(**d)
                    else:
                        function(d)
            else:
                if type(data) == type([]):
                    function(*data)
                elif type(data) == type({}):
                    function(**data)
                else:
                    function(data)
                    
class _EventManager():    
    def __init__(self):
        self.events = {}

    def add_event(self, Event):
        self.events[Event.name] = Event

    def del_event(self, Event):
        self.events.pop(Event.name)

    def connect(self, event, function, data=None):
        self.events[event].add(function, data)

    def disconnect(self, event, function):
        self.events[event].delete(function)

    def signal(self, event, data=None):
        if data is None:
            self.events[event].called()
        else:
            self.events[event].called(data)
            
