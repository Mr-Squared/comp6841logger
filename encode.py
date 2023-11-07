import base64

a = open("hidden.py").read()
ae = base64.b64encode(bytes(a, encoding="utf-8"))

b = open("backdoor.py").read()
be = base64.b64encode(bytes(b, encoding="utf-8"))

c = open("logger.py").read()
ce = base64.b64encode(bytes(c, encoding="utf-8"))

print(ae + be + ce)

print(len(ae))
print(len(ae) + len(be))
