# -*- coding: utf-8 -*-

from __future__ import with_statement

import logging
import os
import threading

core  = None
setup = None
log   = logging.getLogger("log")


class WebServer(threading.Thread):

    def __init__(self, pycore):
        global core

        threading.Thread.__init__(self)
        self.core = pycore
        core = pycore
        self.running = True
        self.server = pycore.config.get("webui", "server")
        self.https = pycore.config.get("webui", "https")
        self.cert = pycore.config.get("ssl", "cert")
        self.key = pycore.config.get("ssl", "key")
        self.host = pycore.config.get("webui", "host")
        self.port = pycore.config.get("webui", "port")

        self.setDaemon(True)


    def run(self):
        import pyload.webui as webinterface
        global webinterface

        reset = False

        if self.https and (not os.exists(self.cert) or not os.exists(self.key)):
            log.warning(_("SSL certificates not found."))
            self.https = False

        if self.server in ("lighttpd", "nginx"):
            log.warning(_("Sorry, we dropped support for starting %s directly within pyLoad") % self.server)
            log.warning(_("You can use the threaded server which offers good performance and ssl,"))
            log.warning(_("of course you can still use your existing %s with pyLoads fastcgi server") % self.server)
            log.warning(_("sample configs are located in the pyload/web/servers directory"))
            reset = True
        elif self.server == "fastcgi":
            try:
                import flup
            except Exception:
                log.warning(_("Can't use %(server)s, python-flup is not installed!") % {
                    "server": self.server})
                reset = True

        if reset or self.server == "lightweight":
            if os.name != "nt":
                try:
                    import bjoern
                except Exception, e:
                    log.error(_("Error importing lightweight server: %s") % e)
                    log.warning(_("You need to download and compile bjoern, https://github.com/jonashaag/bjoern"))
                    log.warning(_("Copy the bjoern.so file to lib/Python/Lib or use setup.py install"))
                    log.warning(_("Of course you need to be familiar with linux and know how to compile software"))
                    self.server = "auto"
            else:
                self.core.log.info(_("Server set to threaded, due to known performance problems on windows."))
                self.core.config.set("webui", "server", "threaded")
                self.server = "threaded"

        if self.server == "threaded":
            self.start_threaded()
        elif self.server == "fastcgi":
            self.start_fcgi()
        elif self.server == "lightweight":
            self.start_lightweight()
        else:
            self.start_auto()


    def start_auto(self):
        if self.https:
            log.warning(_("This server offers no SSL, please consider using `threaded` instead"))

        self.core.log.info(_("Starting builtin webserver: %(host)s:%(port)d") % {"host": self.host, "port": self.port})
        webinterface.run_auto(host=self.host, port=self.port)


    def start_threaded(self):
        if self.https:
            self.core.log.info(
                _("Starting threaded SSL webserver: %(host)s:%(port)d") % {"host": self.host, "port": self.port})
        else:
            self.cert = ""
            self.key = ""
            self.core.log.info(
                _("Starting threaded webserver: %(host)s:%(port)d") % {"host": self.host, "port": self.port})

        webinterface.run_threaded(host=self.host, port=self.port, cert=self.cert, key=self.key)


    def start_fcgi(self):
        self.core.log.info(_("Starting fastcgi server: %(host)s:%(port)d") % {"host": self.host, "port": self.port})
        try:
            webinterface.run_fcgi(host=self.host, port=self.port)

        except ValueError:  #@TODO: Fix https://github.com/pyload/pyload/issues/1145
            pass


    def start_lightweight(self):
        if self.https:
            log.warning(_("This server offers no SSL, please consider using `threaded` instead"))

        self.core.log.info(
            _("Starting lightweight webserver (bjoern): %(host)s:%(port)d") % {"host": self.host, "port": self.port})
        webinterface.run_lightweight(host=self.host, port=self.port)


    def quit(self):
        self.running = False
