import usocket as socket
import ssl


sock = socket.socket()
#sock.connect(("google.com", 443))
addr = socket.getaddrinfo("google.com", 443)[0][-1]
sock.connect(addr)

ctx = ssl.SSLContext()

ssl_sock = ctx.wrap_socket(sock)
ssl_sock.write(b"GET /foo HTTP/1.0\r\n\r\n")

while True:
    data = ssl_sock.read()
    print(data)
    if not data:
        break
