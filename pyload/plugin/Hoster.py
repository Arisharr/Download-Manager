# -*- coding: utf-8 -*-

from pyload.plugin.Plugin import Plugin


def getInfo(self):
        #result = [ .. (name, size, status, url) .. ]
        return


class Hoster(Plugin):
    __name__    = "Hoster"
    __type__    = "hoster"
    __version__ = "0.02"

    __pattern__ = r'^unmatchable$'
    __config__  = []  #: [("name", "type", "desc", "default")]

    __description__ = """Base hoster plugin"""
    __license__     = "GPLv3"
    __authors__     = [("mkaay", "mkaay@mkaay.de")]