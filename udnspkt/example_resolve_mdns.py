import sys
import uio
import usocket

import udnspkt


s = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
dns_addr = usocket.getaddrinfo("224.0.0.251", 5353)[0][-1]


def resolve(domain, is_ipv6):
    buf = uio.BytesIO(48)
    udnspkt.make_req(buf, domain, is_ipv6, unicast=True)
    v = buf.getvalue()
    print("# query: ", v)
    s.sendto(v, dns_addr)

    resp = s.recv(1024)
    print("# resp:", resp)
    buf = uio.BytesIO(resp)

    addr = udnspkt.parse_resp(buf, is_ipv6)
    print("# bin addr:", addr)
    if addr:
        print("addr:", usocket.inet_ntop(usocket.AF_INET6 if is_ipv6 else usocket.AF_INET, addr))


host = sys.argv[1]
if not host.endswith(".local"):
    print("WARNING: mDNS addresses should end with .local, you unlikely will get a response\n")

print(host, "IPv4")
resolve(host, False)
print()
print(host, "IPv6")
resolve(host, True)
