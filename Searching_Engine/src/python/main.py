from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from handler import *

# handlers
direct = [
    (r"/", home_page),
    (r"/search", search),
    (r"/autocomplete", Autocomplete),
]


def main():
    application = Application(direct)
    http_server = HTTPServer(
        application,
    )

    # project to port 81 for external IP
    http_server.listen(8888)
    IOLoop.instance().start()


if __name__ == "__main__":
    main()
