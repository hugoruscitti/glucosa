print "********* VERSION falsa de gtk, para permitir que ande el build de readthedocs."

class FakeGDK(object):

    def __init__(self):
        pass

    def __getattr__(self, attr):
        pass

gdk = FakeGDK()
