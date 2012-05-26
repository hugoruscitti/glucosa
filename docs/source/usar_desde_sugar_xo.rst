Cómo usar glucosa desde Sugar XO
================================

Para realizar puebas, y conocer la bilioteca, puedes
descargar todo el código del repositorio y ejecutar
nuestros demos.

Abre el entorno Sugar, ya sea desde una máquina XO, un
emulador o máquina virtual. El proceso es el mismo en
cualquier caso:

.. image:: images/entorno.png

Una vez iniciado, elige la vista de lista:

.. image:: images/list_view.png

y luego abre la consola:

.. image:: images/open_console.png

Ahí, tienes que escribir algunos comandos para
obtener todo el código de glucosa.

Si tienes ``git`` instalado, el comando para descargar
glucosa es el siguiente::

    git clone git://github.com/hugoruscitti/glucosa.git

En caso contrario, utiliza el siguiente comando::

    wget https://github.com/hugoruscitti/glucosa/tarball/master
    tar xvzf master

Y luego, de cualquiera de las dos formas, solo tienes que ingresar
en el directorio creado y ejecutar el script demostración::

    cd glucosa
    python demo.py

En la pantalla aparecerá un pequeño ejemplo indicado
que todo a funcionado bien:

.. image:: images/resultado.png

Fecilitaciones!
