# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, asynchronous
from tornado.concurrent import Future
from tornado.gen import chain_future
from tornado.options import define, options, parse_command_line

# Importo los manejadores soportados.
from plugins.simple import SimpleHandler
from plugins.maps import MapHandler

# Defino las opciones soportadas en linea de comandos
define("port",    default=8888,       help="Run on the given port", type=int)
define("botname", default="slackbot", help="Robot name",            type=str)
define("webhook", default="",         help="Slack Webhook URL",     type=str)

# Registro donde se almacenan los plugins soportados
REGISTRY = dict()

# Cargo el gestor de mensajes
class MainHandler(RequestHandler):

    @asynchronous
    def post(self):
        self._manage()

    def _commit(self, future):
        """Callback que finaliza la peticion empezada por _manage"""
        if future.exception():
            self.write("*Error:* %s" % str(future.exception()))
        else:
            self.write(future.result())
        self.finish()

    def _manage(self, reg=REGISTRY):
        # Almaceno los parametros del POST en un dict()
        data    = dict((k, self.get_argument(k))
                  for k in self.request.arguments.keys())
        # Utilizo la primera palabra como orden
        command = data['text'].strip().split()
        head    = command.pop(0) if command else None
        # Recupero el handler asociado a la orden
        handler = reg.get(head, None) if head else None
        future  = Future()
        print("data: %s" % str(data))
        if not handler:
            # Si no hay orden, resuelvo el resultado inmediatamente
            future.set_result(
                "Lista de comandos soportados: %s" % ", ".join(reg.keys())
            )
        else:
            # Si hay orden, la ejecuto y encadeno mi propio
            # resultado al resultado de la orden
            chain_future(handler(command, data), future)
        # Cuando se resuelva la peticion, escribimos el resultado
        IOLoop.current().add_future(future, self._commit)

    @asynchronous
    def get(self):
        #self.write("Slackbot accepts only POST messages")
        #simplify initial debug
        self._manage()


application = Application([
    (r"/", MainHandler),
    (r"/slack", MainHandler),
])

if __name__ == "__main__":

    # Registra los manejadores soportados
    parse_command_line()
    REGISTRY['ping'] = SimpleHandler('pong!')
    REGISTRY['map']  = MapHandler(options.botname, options.webhook)

    # Inicia la aplicacion
    application.listen(options.port)
    IOLoop.instance().start()
