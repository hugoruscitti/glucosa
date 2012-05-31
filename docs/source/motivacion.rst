Motivación
----------

Existen muchas bibliotecas para hacer videojuegos, incluso la mayoría son
excelentes bibliotecas, completas y atractivas. Entonces, ¿Por qué hacer una nueva biblioteca?.

Glucosa es una biblioteca impulsada por dos necesidades, por una lado: queríamos
tener una biblioteca pequeña y fácil de utilizar para proyectos sencillos. Y por otro lado, los creadores
de glucosa también estamos trabajando para llevar `pilas-engine <a href='http://www.pilas-engine.com.ar'>`_
al sistema **sugar xo**, y necesitábamos algo de código base para comenzar.

Así que nos preguntamos, ¿por qué no?.


Instalación
-----------

Existen varias formas de instalar glucosa en tu sistema. Aquí veremos dos formas de instalar la biblioteca:

Una opción es clonar el repositorio **git** completo::

    git clone git@github.com:hugoruscitti/glucosa.git

Dentro del directorio que se generará, encontrarás ejemplos y el archivo mas importante para
que todo funcione: *glucosa.py*.

Otra opción, sobretodo cuando estás usando la biblioteca dentro de otro
proyecto, es descargar solamente los archivos básicos para que glucosa funcione::

    wget https://raw.github.com/hugoruscitti/glucosa/master/glucosa.py
    wget https://raw.github.com/hugoruscitti/glucosa/master/demo.py

Listo, ahora puedes probar nuestro programa de ejemplo::

    python demo.py
