#Basic encryption test
import re
import random

def powMod(x, y, z):
    result = 1
    while y:
        if y % 2 == 1:
            result = result * x % z
        y >>= 1
        x = x * x % z
    return result

##dataIn = "".join([chr(random.randint(65,90)) for x in range(100000)])#input()
dataIn = input()
dataInList = list(dataIn)

pubKey = 4363*2539
sharedKey = 17
encry = []

privateKey = 651221
for m in dataInList:
    message = ord(m)
    encry.append(hex((message**sharedKey)%pubKey))

encry = "".join(encry)
#print(encry)

#-----------------------DATA TRANSFER-------------#

#-----------------------Intercept-----------------#
##intercept = []
encry = encry.split("0x")[1:]
##for x in encry:
##    intercept.append(chr(int(x,16)))
##
##print("".join(intercept))
#-----------------------End-----------------------#
dataOut = []
##encry = re.findall("....", encry)
for c in encry:

    dataOut.append(chr(pow_mod(int(c,16), privateKey, pubKey)))

print("".join(dataOut))

if "".join(dataOut) == dataIn:print("Good")
