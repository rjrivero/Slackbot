import tornado.ioloop
import tornado.web
import tornado.escape

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)


# Formato del POST recibido:
#
#token=bT1Oqy4c66ECzG5KNFFFGGjg
#team_id=T0001
#team_domain=example
#channel_id=C2147483705
#channel_name=test
#timestamp=1355517523.000005
#user_id=U2147483697
#user_name=Steve
#text=googlebot: What is the air-speed velocity of an unladen swallow?
#trigger_word=googlebot:

class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("Slackbot accepts only POST messages")

    def post(self):
        data = tornado.escape.json_decode(self.request_body)
        print("data: %s" % str(data))

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    tornado.options.parse_command_line()
    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

