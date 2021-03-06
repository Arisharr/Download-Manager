# -*- coding: utf-8 -*-

import re

from pyload.plugin.Account import Account


class YibaishiwuCom(Account):
    __name    = "YibaishiwuCom"
    __type    = "account"
    __version = "0.02"

    __description = """115.com account plugin"""
    __license     = "GPLv3"
    __authors     = [("zoidberg", "zoidberg@mujmail.cz")]


    ACCOUNT_INFO_PATTERN = r'var USER_PERMISSION = {(.*?)}'


    def loadAccountInfo(self, user, req):
        # self.relogin(user)
        html = req.load("http://115.com/", decode=True)

        m = re.search(self.ACCOUNT_INFO_PATTERN, html, re.S)
        premium = m and 'is_vip: 1' in m.group(1)
        validuntil = trafficleft = (-1 if m else 0)
        return dict({"validuntil": validuntil, "trafficleft": trafficleft, "premium": premium})


    def login(self, user, data, req):
        html = req.load("http://passport.115.com/?ac=login",
                        post={"back": "http://www.115.com/",
                              "goto": "http://115.com/",
                              "login[account]": user,
                              "login[passwd]": data['password']},
                        decode=True)

        if not 'var USER_PERMISSION = {' in html:
            self.wrongPassword()
