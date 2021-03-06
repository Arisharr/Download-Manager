# -*- coding: utf-8 -*-

import re
import time

from pyload.plugin.Account import Account


class FilejungleCom(Account):
    __name    = "FilejungleCom"
    __type    = "account"
    __version = "0.12"

    __description = """Filejungle.com account plugin"""
    __license     = "GPLv3"
    __authors     = [("zoidberg", "zoidberg@mujmail.cz")]


    login_timeout = 60

    URL = "http://filejungle.com/"
    TRAFFIC_LEFT_PATTERN = r'"/extend_premium\.php">Until (\d+ \w+ \d+)<br'
    LOGIN_FAILED_PATTERN = r'<span htmlfor="loginUser(Name|Password)" generated="true" class="fail_info">'


    def loadAccountInfo(self, user, req):
        html = req.load(self.URL + "dashboard.php")
        m = re.search(self.TRAFFIC_LEFT_PATTERN, html)
        if m:
            premium = True
            validuntil = time.mktime(time.strptime(m.group(1), "%d %b %Y"))
        else:
            premium = False
            validuntil = -1

        return {"premium": premium, "trafficleft": -1, "validuntil": validuntil}


    def login(self, user, data, req):
        html = req.load(self.URL + "login.php",
                        post={"loginUserName": user,
                              "loginUserPassword": data['password'],
                              "loginFormSubmit": "Login",
                              "recaptcha_challenge_field": "",
                              "recaptcha_response_field": "",
                              "recaptcha_shortencode_field": ""},
                        decode=True)

        if re.search(self.LOGIN_FAILED_PATTERN, html):
            self.wrongPassword()
