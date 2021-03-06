import math
import re

op = open("Ham.txt", "r")
toHam = op.read()

inputRaw = [str(bin(ord(x))) for x in toHam]
for x in inputRaw:
    if len(x) == 8:
        y = "0" + x
        inputRaw[inputRaw.index(x)] = y

inputRaw = "".join(inputRaw)
inputRaw = inputRaw.replace("b", "")

def placeHold(string, length):
    return string[:length] + "%" + string[length:]

def calcParity(string, pos):
    parity = re.findall((''.join('.' for x in range(0,pos))+'?'),string[pos-1:])
    if parity == []:
        parity = string[pos-1:]
    else:
        for x in range(1,len(parity)):
            if x % 2 != 0:
                parity[x] = ""

    parity ="".join(parity)
    if parity.count("1") % 2 == 0:
        return "0"
    else:
        return "1"

inputRaw = re.findall("........", inputRaw)
for y in inputRaw:
    i = y
    iterate =  math.ceil(math.log(len(i),2))+1

    for x in range(0, iterate):
        i = placeHold(i, (2**x)-1)

    iterate =  math.ceil(math.log(len(i),2))

    for x in range(0, iterate):
        toAdd = calcParity(i,(2**x))
        i = list(i)
        i[(2**x)-1] = toAdd
        i = "".join(i)

    inputRaw[inputRaw.index(y)] = i

inputRaw = "".join(inputRaw)
op.close()

op = open("Complete.txt", "w")
op.write("%s" %inputRaw)
op.close()
