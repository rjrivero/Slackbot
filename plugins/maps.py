# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from tornado.concurrent import Future
from tornado.gen import coroutine
from tornado.escape import url_escape, json_encode
from tornado.httpclient import AsyncHTTPClient


class MapCommand(object):

    """Analiza un comando y genera los datos adecuados para Slack"""

    # Titulo del mensaje enviado a Slack.
    #
    # Debe recibir dos parametros de formateo:
    # - 'query': El texto de la query del usuario, en formato legible
    # - 'address': El texto de la query en formato urlencode
    TITLE    = u"Mapa de *{query}* (<http://maps.google.es?q={address}|Ver en Google Maps>)"
    
    # Dimensiones de la imagen. Maximo soportado por Slack: 400x500
    # (https://api.slack.com/docs/attachments)
    IMG_SIZE = u"400x500"

    # URL de la imagen
    #
    # Debe recibir dos parametros de formateo:
    # - 'size': El AnchoxAlto de la imagen a generar (ej: "400x400")
    # - 'address': El texto de la query en formato urlencode
    API_URL  = u"http://maps.googleapis.com/maps/api/staticmap?size={size}&markers={address}&sensor=false"

    def __init__(self, command, data):

        query  = u" ".join(command)
        self._params = {
            "query":   query,
            "address": url_escape(query),
            "size":    MapCommand.IMG_SIZE,
        }

    def payload(self):
        """Genera el payload a enviar a Slack"""

        title   = MapCommand.TITLE.format(**self._params)
        api_url = MapCommand.API_URL.format(**self._params)
        return {
            "text": title,
            "icon_emoji": u":earth_asia:",
            "unfurl_links": True,
            "attachments": [
                {
                    "fallback": u"Google Static Maps",
                    "color": "good",
                    "image_url": api_url,
                }
            ]
        }


class MapHandler(object):

    """Manejador del comando "map".

    Genera un enlace a static google maps, centrado en la zona
    que nos mandan en el texto.
    """

    def __init__(self, botname, webhook):
        self._botname = botname
        self._webhook = webhook
        self._title   = u"Mapa de {search} (<{url}|Ver en Google Maps>)"

    def _done(self):
        future = Future()
        future.set_result("")
        return future

    def __call__(self, command, data):
        """Empuja a slack un mensaje con un mapa de google maps"""

        payload = MapCommand(command, data).payload()
        payload['channel']    = data['channel_name']
        payload['username']   = self._botname
        payload['icon_emoji'] = u":earth_asia:"

        body   = json_encode(payload)
        client = AsyncHTTPClient()
        client.fetch(self._webhook, method='POST', headers=None, body=body)

        # Podria devolver el Futuro que genera "fetch", pero entonces
        # la peticion no terminaria hasta que Slack nos responda, y tampoco
        # tenemos necesidad de esperar.
        return self._done()
