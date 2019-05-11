from selectors import *


f = open(0, "rb")

p = DefaultSelector()
print(p)
print(p.register(f, EVENT_READ, "userdata"))

for r in p.select():
    print(r)
