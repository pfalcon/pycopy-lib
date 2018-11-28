import uwwwauth


# Example from https://tools.ietf.org/html/rfc2617#section-2

headers = {"WWW-Authenticate": 'Basic realm="WallyWorld"'}
auth_req = uwwwauth.parse_auth_req(headers["WWW-Authenticate"])
print(auth_req)
assert auth_req == {'realm': 'WallyWorld', 'type': 'Basic'}

resp = uwwwauth.basic_resp("Aladdin", "open sesame")
print(repr(resp))
assert resp == "Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=="

resp = uwwwauth.auth_resp(headers["WWW-Authenticate"], "Aladdin", "open sesame")
assert resp == "Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=="

auther = uwwwauth.WWWAuth("Aladdin", "open sesame")
resp = auther.resp(headers["WWW-Authenticate"], "GET", "/foo/bar")
assert resp == "Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=="


# Example from https://tools.ietf.org/html/rfc2069#section-2.4, with errata in
# https://www.rfc-editor.org/errata_search.php?rfc=2069

headers = {"WWW-Authenticate": 'Digest    realm="testrealm@host.com", ' \
    'nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093", ' \
    'opaque="5ccc069c403ebaf9f0171e9517f40e41"'}

auth_req = uwwwauth.parse_auth_req(headers["WWW-Authenticate"])
print(auth_req)

assert auth_req == {
    'type': 'Digest',
    'nonce': 'dcd98b7102dd2f0e8b11d0f600bfb0c093',
    'realm': 'testrealm@host.com',
    'opaque': '5ccc069c403ebaf9f0171e9517f40e41'
}

resp = uwwwauth.auth_resp(headers["WWW-Authenticate"], "Mufasa", "CircleOfLife", "GET", "/dir/index.html")
assert 'response="1949323746fe6a43ef61f9606e7febea"' in resp

auther = uwwwauth.WWWAuth("Mufasa", "CircleOfLife")
resp = auther.resp(headers["WWW-Authenticate"], "GET", "/dir/index.html")
print(resp)
assert 'response="1949323746fe6a43ef61f9606e7febea"' in resp


try:
    resp = auther.resp("foo", "GET", "/dir/index.html")
    assert False
except ValueError:
    pass
