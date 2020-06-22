from ussl import *
import ussl as _ussl

# Constants
for sym in "CERT_NONE", "CERT_OPTIONAL", "CERT_REQUIRED":
    if sym not in globals():
        globals()[sym] = object()


PROTOCOL_TLS = 2


class SSLContext:

    def __init__(self, protocol=PROTOCOL_TLS):
        self._ctx = _ussl.SSLContext(protocol)

    def wrap_socket(
        self, sock, server_side=False, do_handshake_on_connect=True,
        suppress_ragged_eofs=True, server_hostname=None, session=None
    ):
        return self._ctx.wrap_socket(
            sock,
            server_hostname=server_hostname,
            do_handshake=do_handshake_on_connect,
        )


def wrap_socket(
    sock, keyfile=None, certfile=None, server_side=False, cert_reqs=CERT_NONE,
    ssl_version=PROTOCOL_TLS, ca_certs=None, do_handshake_on_connect=True,
    suppress_ragged_eofs=True, ciphers=None
):
    ctx = SSLContext(ssl_version)

    kw = {}
    key = cert = None
    if keyfile is not None:
        with open(keyfile, "rb") as f:
            key = f.read()
    if certfile is not None:
        with open(certfile, "rb") as f:
            cert = f.read()
    if key or cert:
        ctx.set_cert_key(cert, key)

    if ca_certs is not None:
        raise NotImplementedError

    kw = {}
    if server_side is not False:
        kw["server_side"] = server_side
    if cert_reqs is not CERT_NONE:
        kw["cert_reqs"] = cert_reqs
    return ctx.wrap_socket(sock, **kw)
