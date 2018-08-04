# Requires a sample server from CPython docs:
# https://docs.python.org/3.5/library/xmlrpc.client.html
import xmlrpc.client

proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")
print(proxy.is_even(3))
print(proxy.is_even(100))
