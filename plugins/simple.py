# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from tornado.concurrent import Future

class SimpleHandler(object):

    """Implementacion de referencia de un manejador de comandos.
    
    Un manejador es un simple objeto "callable" que debe recibir los
    datos de un POST hecho por slack, y devolver un "Future". El resultado
    de ese "Future" es lo que se entrega a slack.

    Los datos que entrega Slack consisten en un diccionario con los
    siguientes elementos, todos unicode:

    - 'user_id'
    - 'channel_id'
    - 'text'
    - 'token'
    - 'channel_name'
    - 'team_id'
    - 'command'
    - 'team_domain'
    - 'user_name'

    Adicionalmente, el servidor web descompone el texto de la orden
    ('text') en palabras separadas por espacios:

    - La primera palabra identifica el manejador que se va a encargar
      de servir la orden.
    - El resto de palabras se pasan al manejador tal cual.
    """

    def __init__(self, msg):
        """Constructor del manejador simple.

        Este manejador se limita a responder a Slack con el mensaje dado.
        """
        self._msg = msg

    def __call__(self, command, data):
        """Genera la respuesta a la peticion.
        
        En este manejador simple, solo devolvemos un texto estatico,
        el proporcionado en el constructor.
        
        - command: una lista con los argumentos del comando,
                   excluido el primero (la orden)
        - data: todos los parametros entregados por Slack.
        """
        future = Future()
        future.set_result(self._msg)
        return future

