# -*- coding: UTF-8 -*-

import sys
sys.path.append("..")

import pygtk
pygtk.require('2.0')
import gtk

import glucosa

class MainWindow:
    
    def destroy(self, widget, data=None):
        gtk.main_quit()
        
    def cambio_rotacion(self, adjustment):
        self.sprite.set_rotation(adjustment.get_value())
        
    def cambio_escala(self, adjustment):
        self.sprite.set_scale(adjustment.get_value())

    def cambio_posicion_x(self, adjustment):
        self.sprite.set_pos(adjustment.get_value(), -1)
    
    def cambio_posicion_y(self, adjustment):
        self.sprite.set_pos(-1, adjustment.get_value())
    

    def crear_ventana(self):
        
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_resizable(False)
        self.window.set_size_request(400, 400)
        self.window.set_title("Glucosa Demo con GTK")        
        self.window.connect("destroy", self.destroy)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_icon_from_file("tux.png")   
        
        self.vbox = gtk.VBox(False, 6)     
        
    def crear_area_dibujo(self): 
        self.area = glucosa.GameArea()
        self.area.set_size_request(400,150)
    
    
    def crear_barras_desplazamiento(self):
        # ----- ROTACION ------

        # Contenedor horizontal para la rotación.
        hbox_rotation = gtk.HBox(True, 2)
        # Etiqueta para la rotación
        label_rotation = gtk.Label("Rotation: ")
        
        # Ajustes para para barra de rotación.
        # Incrementa de uno en uno hasta una rotación máxima de 360. 
        adjustment_rotation = gtk.Adjustment(value=0, lower=0, upper=361, 
                                             step_incr=1, page_incr=1, 
                                             page_size=1)
        # Creamos la barra de rotación.
        hscale_rotation = gtk.HScale(adjustment=adjustment_rotation)
        
        # Conectamos el evento de cambio de valor a nuestro método.
        adjustment_rotation.connect("value_changed", self.cambio_rotacion)
        
        # Agregamos la etiqueta y la barra al contenedor.
        hbox_rotation.add(label_rotation)
        hbox_rotation.add(hscale_rotation)
        
        
        # ----- ESCALA ------

        # Contenedor horizontal para la escala.
        hbox_scale = gtk.HBox(True, 2)
        # Etiqueta para la rotación
        label_scale = gtk.Label("Scale: ")
        
        # Ajustes para para barra de escala.
        # Incrementa hasta una escala máxima de 4. 
        adjustment_scale = gtk.Adjustment(value=1, lower=1, upper=4, 
                                             step_incr=0.2, page_incr=0.2, 
                                             page_size=1)
        # Creamos la barra de escala.
        hscale_scale = gtk.HScale(adjustment=adjustment_scale)
        
        # Conectamos el evento de cambio de valor a nuestro método.
        adjustment_scale.connect("value_changed", self.cambio_escala)
        
        # Agregamos la etiqueta y la barra al contenedor.
        hbox_scale.add(label_scale)
        hbox_scale.add(hscale_scale)
        
        
        # ----- POSICION X ------

        # Contenedor horizontal para la posición.
        hbox_x_position = gtk.HBox(True, 2)
        # Etiqueta para la posición
        label_x_position = gtk.Label("Posicion X: ")
        
        # Ajustes para para barra de posición.
        # Incrementa de uno en uno hasta una posición máxima de 400. 
        adjustment_x_position = gtk.Adjustment(value=200, lower=0, upper=401, 
                                             step_incr=1, page_incr=1, 
                                             page_size=1)
        # Creamos la barra de posición.
        hscale_x_position = gtk.HScale(adjustment=adjustment_x_position)
        
        # Conectamos el evento de cambio de valor a nuestro método.
        adjustment_x_position.connect("value_changed", self.cambio_posicion_x)
        
        # Agregamos la etiqueta y la barra al contenedor.
        hbox_x_position.add(label_x_position)
        hbox_x_position.add(hscale_x_position)
        
        
        # ----- POSICION Y ------

        # Contenedor horizontal para la posición.
        hbox_y_position = gtk.HBox(True, 2)
        # Etiqueta para la posición
        label_y_position = gtk.Label("Posicion Y: ")
        
        # Ajustes para para barra de posición.
        # Incrementa de uno en uno hasta una posición máxima de 150. 
        adjustment_y_position = gtk.Adjustment(value=75, lower=0, upper=151, 
                                             step_incr=1, page_incr=1, 
                                             page_size=1)
        # Creamos la barra de posición.
        hscale_y_position = gtk.HScale(adjustment=adjustment_y_position)
        
        # Conectamos el evento de cambio de valor a nuestro método.
        adjustment_y_position.connect("value_changed", self.cambio_posicion_y)
        
        # Agregamos la etiqueta y la barra al contenedor.
        hbox_y_position.add(label_y_position)
        hbox_y_position.add(hscale_y_position)
        
        self.vbox.add(self.area)
        self.vbox.add(hbox_rotation)
        self.vbox.add(hbox_scale)
        self.vbox.add(hbox_x_position)
        self.vbox.add(hbox_y_position)
        
    
    def __init__(self):
        
        # Creamos al ventana principal
        self.crear_ventana()

        # Creamos el DrawingArea donde Glucosa deibujara.
        self.crear_area_dibujo()
        
        # Creamos las barras de desplazamiento para cambiar los valores 
        # del Sprite.
        self.crear_barras_desplazamiento()
        
        # Añadimos los controles a la ventana.
        label_Glucosa = gtk.Label("Glucosa - http://glucosa.readthedocs.org/en/latest/")        
        self.vbox.add(label_Glucosa)        
        self.window.add(self.vbox)
        
        # Mostramos los controles.
        self.window.show_all()
        
        # --- CLUCOSA ---
            
        image = glucosa.Image('../data/glucosa_logo.png')
        self.sprite = glucosa.Sprite(image, 200, 75, 18, 18)
        self.sprite.set_anchor(30, 38)
        self.area.add_sprite(self.sprite)

    def main(self):
        gtk.main()
        
if __name__ == "__main__":
    
    mainWindow = MainWindow()
    mainWindow.main()
