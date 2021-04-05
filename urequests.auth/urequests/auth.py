# (c) 2021 Paul Sokolovsky, MIT license, https://github.com/pfalcon/pycopy-lib
import uwwwauth


class HTTPBasicAuth:
    def __init__(self, user, passwd):
        self.auth = uwwwauth.basic_resp(user, passwd)

    def __call__(self, r):
        r.headers["Authorization"] = self.auth
        return r
