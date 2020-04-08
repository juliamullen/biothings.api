"""
    Biothings Web API

    Run API:

    1a. with default settings:

        # serve all data on localhost:9200
        # may be used for testing and development

        from biothings.web import BiothingsAPI
        api = BiothingsAPI()
        api.start()

    1b. with a customized config module:

        # allow detailed configuration of apis
        # this is similar to how the hub starts web apis

        from biothings.web import BiothingsAPI
        import config
        api = BiothingsAPI(config)
        api.start()

    2. with default command line options:

        # by defualt looks for a 'config.py' under cwd
        # similar to discovery and crawler biothings apps

        from biothings.web.index_base import main
        if __name__ == '__main__':
            main()

    3. with application template framework. # TODO

    On top of the common ways described above, you can specify
    the customized config module in the following ways:

    1. a python module already imported

    2. a fully qualified name to import, for example:
     - 'config'
     - 'app.config.dev'

    3. a file path to a python module, for example:
     - '../config.py'
     - '/home/ubuntu/mygene/config.py'
     - 'C:\\Users\\Biothings\\mygene\\config.py'

    4. explicitly specify None or '' to use default.

    See below for additional configurations like
    using an external asyncio event loop.
"""

import logging

import tornado.httpserver
import tornado.ioloop
import tornado.web

from biothings.web.settings import BiothingESWebSettings


class BiothingsAPI():
    """
    Configure a Biothings Web API Server.

    There are three parts to it:
    * A biothings config module that defines the API handlers.
    * Additional Tornado handlers and application settings.
    * An asyncio event loop to run the tornado application.

    The API can be started with:
    * An external event loop by calling get_server()
    * A default tornado event loop by calling start()

    Unless started externally, debug mode:
    * Sets proper logging levels for root logger and es,
    * Enables debug mode on tornado except for autoreload,
    * Disables integrated tracking and error monitoring.
    """

    def __init__(self, config_module=None):
        self.config = BiothingESWebSettings(config_module)
        self.handlers = []
        self.settings = dict(autoreload=False)
        self.debug = True
        self.host = None

    @staticmethod
    def use_curl():
        """
        Use curl implementation for tornado http clients.
        More on https://www.tornadoweb.org/en/stable/httpclient.html
        """
        tornado.httpclient.AsyncHTTPClient.configure(
            "tornado.curl_httpclient.CurlAsyncHTTPClient")

    def update(self, **settings):
        """
        Update Tornado application settings. More on:
        https://www.tornadoweb.org/en/stable/web.html \
        #tornado.web.Application.settings
        """
        self.settings.update(settings)

    def configure_debug_mode(self):
        """
        Override to define additional debug settings.
        For example, add some handlers in debug mode.
        """
        # About debug mode in tornado:
        # https://www.tornadoweb.org/en/stable/guide/running.html \
        # #debug-mode-and-automatic-reloading
        if self.debug:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.INFO)

    def get_server(self):
        """
        Run API in an external event loop.
        """
        settings = dict(self.settings)
        settings.update(self.config.generate_app_settings(self.debug))
        handlers = self.config.generate_app_handlers(self.handlers)
        webapp = tornado.web.Application(handlers, **settings)
        server = tornado.httpserver.HTTPServer(webapp, xheaders=True)
        return server

    def start(self, port=8000):
        """
        Run API in the default event loop.
        """
        self.configure_debug_mode()

        http_server = self.get_server()
        http_server.listen(port, self.host)

        logging.info('Server is running on "%s:%s"...',
                     self.host or '0.0.0.0', port)

        loop = tornado.ioloop.IOLoop.instance()
        loop.start()


BiothingsAPIApp = BiothingsAPI
