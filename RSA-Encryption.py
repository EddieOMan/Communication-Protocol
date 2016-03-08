#Basic encryption test
import re
import random

dataIn = "".join([chr(random.randint(64,90)) for x in range(100000)])#input()
dataInList = list(dataIn)

pubKey = 13*17
sharedKey = 5
encry = []

privateKey = 77
for m in dataInList:
    message = ord(m)
    encry.append(hex((message**sharedKey)%pubKey))

encry = "".join(encry)
#print(encry)

#-----------------------DATA TRANSFER-------------#

#-----------------------Intercept-----------------#
intercept = []
encry = re.findall("....", encry)
for x in encry:
    intercept.append(chr(int(x,16)))

#print("".join(intercept))
#-----------------------End-----------------------#
dataOut = []
##encry = re.findall("....", encry)
for c in encry:
    dataOut.append(chr((int(c,16)**privateKey)%pubKey))

#print("".join(dataOut))

if "".join(dataOut) == dataIn:print("Good")
