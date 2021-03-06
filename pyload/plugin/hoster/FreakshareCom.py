# -*- coding: utf-8 -*-

import re

from pyload.plugin.Hoster import Hoster
from pyload.plugin.captcha.ReCaptcha import ReCaptcha
from pyload.plugin.internal.SimpleHoster import secondsToMidnight


class FreakshareCom(Hoster):
    __name    = "FreakshareCom"
    __type    = "hoster"
    __version = "0.40"

    __pattern = r'http://(?:www\.)?freakshare\.(net|com)/files/\S*?/'

    __description = """Freakshare.com hoster plugin"""
    __license     = "GPLv3"
    __authors     = [("sitacuisses", "sitacuisses@yahoo.de"),
                       ("spoob", "spoob@pyload.org"),
                       ("mkaay", "mkaay@mkaay.de"),
                       ("Toilal", "toilal.dev@gmail.com")]


    def setup(self):
        self.multiDL = False
        self.req_opts = []


    def process(self, pyfile):
        self.pyfile = pyfile

        pyfile.url = pyfile.url.replace("freakshare.net/", "freakshare.com/")

        if self.account:
            self.html = self.load(pyfile.url, cookies=False)
            pyfile.name = self.get_file_name()
            self.download(pyfile.url)

        else:
            self.prepare()
            self.get_file_url()

            self.download(pyfile.url, post=self.req_opts)

            check = self.checkDownload({"bad"           : "bad try",
                                        "paralell"      : "> Sorry, you cant download more then 1 files at time. <",
                                        "empty"         : "Warning: Unknown: Filename cannot be empty",
                                        "wrong_captcha" : "Wrong Captcha!",
                                        "downloadserver": "No Downloadserver. Please try again later!"})

            if check == "bad":
                self.fail(_("Bad Try"))

            elif check == "paralell":
                self.setWait(300, True)
                self.wait()
                self.retry()

            elif check == "empty":
                self.fail(_("File not downloadable"))

            elif check == "wrong_captcha":
                self.invalidCaptcha()
                self.retry()

            elif check == "downloadserver":
                self.retry(5, 15 * 60, _("No Download server"))


    def prepare(self):
        pyfile = self.pyfile

        self.download_html()

        if not self.file_exists():
            self.offline()

        self.setWait(self.get_waiting_time())

        pyfile.name = self.get_file_name()
        pyfile.size = self.get_file_size()

        self.wait()

        return True


    def download_html(self):
        self.load("http://freakshare.com/index.php", {"language": "EN"})  #: Set english language in server session
        self.html = self.load(self.pyfile.url)


    def get_file_url(self):
        """ returns the absolute downloadable filepath
        """
        if not self.html:
            self.download_html()
        if not self.wantReconnect:
            self.req_opts = self.get_download_options()  #: get the Post options for the Request
            # file_url = self.pyfile.url
            # return file_url
        else:
            self.offline()


    def get_file_name(self):
        if not self.html:
            self.download_html()

        if not self.wantReconnect:
            m = re.search(r"<h1\sclass=\"box_heading\"\sstyle=\"text-align:center;\">([^ ]+)", self.html)
            if m:
                file_name = m.group(1)
            else:
                file_name = self.pyfile.url

            return file_name
        else:
            return self.pyfile.url


    def get_file_size(self):
        size = 0
        if not self.html:
            self.download_html()

        if not self.wantReconnect:
            m = re.search(r"<h1\sclass=\"box_heading\"\sstyle=\"text-align:center;\">[^ ]+ - ([^ ]+) (\w\w)yte", self.html)
            if m:
                units = float(m.group(1).replace(",", ""))
                pow = {'KB': 1, 'MB': 2, 'GB': 3}[m.group(2)]
                size = int(units * (2 ** 20) ** pow)

        return size


    def get_waiting_time(self):
        if not self.html:
            self.download_html()

        if "Your Traffic is used up for today" in self.html:
            self.wantReconnect = True
            return secondsToMidnight(gmt=2)

        timestring = re.search('\s*var\s(?:downloadWait|time)\s=\s(\d*)[\d.]*;', self.html)
        if timestring:
            return int(timestring.group(1))
        else:
            return 60


    def file_exists(self):
        """ returns True or False
        """
        if not self.html:
            self.download_html()
        if re.search(r"This file does not exist!", self.html):
            return False
        else:
            return True


    def get_download_options(self):
        re_envelope = re.search(r".*?value=\"Free\sDownload\".*?\n*?(.*?<.*?>\n*)*?\n*\s*?</form>",
                                self.html).group(0)  #: get the whole request
        to_sort = re.findall(r"<input\stype=\"hidden\"\svalue=\"(.*?)\"\sname=\"(.*?)\"\s\/>", re_envelope)
        request_options = dict((n, v) for (v, n) in to_sort)

        herewego = self.load(self.pyfile.url, None, request_options)  #: the actual download-Page

        to_sort = re.findall(r"<input\stype=\".*?\"\svalue=\"(\S*?)\".*?name=\"(\S*?)\"\s.*?\/>", herewego)
        request_options = dict((n, v) for (v, n) in to_sort)

        challenge = re.search(r"http://api\.recaptcha\.net/challenge\?k=(\w+)", herewego)

        if challenge:
            re_captcha = ReCaptcha(self)
            (request_options['recaptcha_challenge_field'],
             request_options['recaptcha_response_field']) = re_captcha.challenge(challenge.group(1))

        return request_options
