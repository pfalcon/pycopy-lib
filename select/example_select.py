import select


res = select.select([0], [], [], 1.1)
print(res)
