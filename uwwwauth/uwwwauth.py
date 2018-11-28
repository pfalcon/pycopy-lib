# RFC2617, WWW-Authenticate: Basic/Digest module
# (c) 2018 Paul Sokolovsky, MIT license
import uhashlib
import ubinascii


# Private functions - do not use, will change

def md5_concat(arg1, arg2, arg3):
    h = uhashlib.md5(arg1)
    h.update(b":")
    h.update(arg2)
    if arg3 is not None:
        h.update(b":")
        h.update(arg3)
    return ubinascii.hexlify(h.digest()).decode()


def make_digest_ha1(a1, method, uri, nonce):
    a2 = md5_concat(method, uri, None)
    digest = md5_concat(a1, nonce, a2)
    return digest


def make_digest(realm, username, passwd, method, uri, nonce):
    a1 = md5_concat(username, realm, passwd)
    return make_digest_ha1(a1, method, uri, nonce)


def parse_auth_req(line):
    typ, line = line.split(None, 1)
    d = {"type": typ}
    for kv in line.split(","):
        k, v = kv.split("=", 1)
        assert v[0] == '"' and v[-1] == '"'
        d[k.strip()] = v[1:-1]
    return d


def format_resp(resp_d):
    fields = []
    for k, v in resp_d.items():
        if k in ("type", "passwd"):
            continue
        fields.append('%s="%s"' % (k, v))
    resp_auth = ", ".join(fields)

    resp_auth = "Digest " + resp_auth
    return resp_auth


def _digest_resp(auth_d, username, passwd, method, URL):
    #print(auth_d)

    resp_d = {}
    resp_d["username"] = username
    resp_d["uri"] = URL
    resp_d["realm"] = auth_d["realm"]
    resp_d["nonce"] = auth_d["nonce"]

    digest = make_digest(auth_d["realm"], username, passwd, method, URL, auth_d["nonce"])
    resp_d["response"] = digest
    #print(resp_d)

    return format_resp(resp_d)


# Helper functions - may change

def basic_resp(username, passwd):
    return "Basic " + ubinascii.b2a_base64("%s:%s" % (username, passwd))[:-1].decode()


def auth_resp(auth_line, username, passwd, method=None, URL=None):
    auth_d = parse_auth_req(auth_line)
    if auth_d["type"] == "Basic":
        return basic_resp(username, passwd)
    elif auth_d["type"] == "Digest":
        assert method and URL
        return _digest_resp(auth_d, username, passwd, method, URL)
    else:
        raise ValueError(auth_d["type"])


# Public interface

class WWWAuth:

    def __init__(self, username, passwd):
        self.username = username
        self.passwd = passwd
        self.cached_auth_line = None

    def resp(self, auth_line, method, URL):
        if auth_line.startswith("Basic"):
            return basic_resp(self.username, self.passwd)
        elif auth_line.startswith("Digest"):
            auth_d = parse_auth_req(auth_line)
            if auth_line != self.cached_auth_line:
                self.ha1 = md5_concat(self.username, auth_d["realm"], self.passwd)
            self.cached_auth_line = auth_line
            digest = make_digest_ha1(self.ha1, method, URL, auth_d["nonce"])
            auth_d["username"] = self.username
            auth_d["uri"] = URL
            auth_d["response"] = digest
            return format_resp(auth_d)
        else:
            raise ValueError("Unsupported auth: " + auth_line)
