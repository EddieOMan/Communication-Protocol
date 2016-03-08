import math
foo = int("".join([str((ord(x)^math.floor(11**(1/ord(x))))) for x in list(input())]))
parity = 475

for x in list(str(foo)):
    for y in range(13):
        parity = int(x)>>11 ^ parity

save = (foo ** parity>>int(str(foo)[:4]))

print(hex(int(str(save)[64::-1])))
print(len(str(hex(int(str(save)[64::-1])))))
