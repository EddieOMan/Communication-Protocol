import math
import random
import string
chars = string.ascii_letters + string.digits
salt = "".join(random.choice(chars) for i in range(16))
foo = int("".join([str((ord(x))) for x in list(input()+salt)]))
parity = 473

for x in list(str(foo)):
    parity ^= int(x)<<3

save = (foo ** parity>>int(str(foo)[:4]))

print(str(hex(save))[:256])
print("\n"+salt)
