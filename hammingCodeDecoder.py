import re
import math

op = open("Complete.txt", "r")
inputRaw = op.read()

def checkParity(string, pos):
    endCheck = string[pos-1]
    string = list(string)
    string[pos-1] = "%"
    string = "".join(string)

    parity = re.findall((''.join('.' for x in range(0,pos))+'?'),(string[pos-1:]))
    if parity == []:
        parity = string[pos-1:]
    else:
        for x in range(1,len(parity)):
            if x % 2 != 0:
                parity[x] = ""

    parity ="".join(parity)
    if parity.count("1") % 2 == int(endCheck):
        return 0
    else:
        return pos

y = 0
inputRaw = re.findall("............", inputRaw)
for i in inputRaw:
    iterate =  math.ceil(math.log(len(i),2))
    errors = []

    for x in range(0,iterate):
        result = checkParity(i,(2**x))
        errors.append(result)

    location = 0
    for x in errors:
        if x > 0:
            location += int(x)

    if location > 0:
        response = input("Error in transmition detected, location at byte " + str(y) + "and bit" + str(location) + ".\nShould the program try to auto correct? y/n")
        if response.lower() == "y":
            i = list(i)
            i[location-1] = str(1 - int(i[location-1]))
            i = "".join(i)

    for x in range(0, iterate):
        i = list(i)
        i[(2**x)-1] = "%"
        i = "".join(i)

    inputRaw[y] = i
    y += 1

op.close()
op = open("Output.txt", "w")
inputRaw = "".join(inputRaw)
inputRaw = inputRaw.replace("%", "")
inputRaw = re.findall("........", inputRaw)
for i in [int(x,2) for x in inputRaw]:
    output = chr(i)
    op.write("%s" %output)

op.close()
