import math, re, random, string, socket, os
from tkinter import *
from tkinter import filedialog
#------------------------Initialization-----------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "192.168.0.6"
port = 5555
sock.connect((server,port))
IP = sock.getsockname()[0]


commServer = "COMMAND"
endMess = "EOFEOFEOFX"

#------------------------Tkinter definitions-----------------------
##rootWindow = Tk()
##rootWindow.title("Protocol")
##rootWindow.geometry("512x256")


def logWrite(toWrite):
    #------------------------Data Logging-----------------------
    log = open("logFile.txt", "a")
    log.write(toWrite)
    log.close()

def powMod(x, y, z):
    result = 1
    while y:
        if y % 2 == 1:
            result = result * x % z
        y >>= 1
        x = x * x % z
    return result

def parityFix(binInt):
    binStr = str(binInt).replace("0b","")
    output = ""
    if len(binStr) < 12:
        for x in range(12-len(binStr)):
            output += "0"

    return output + binStr

def hashPassword(password, salt = ""):
    #------------------------Hashing-----------------------
    if salt == "":
        chars = string.ascii_letters + string.digits
        salt = "".join(random.choice(chars) for i in range(16))

    foo = int("".join([str((ord(x))) for x in list(password+salt)]))
    parity = 473

    for x in list(str(foo)):
        parity ^= int(x)<<3

    save = (foo ** parity>>int(str(foo)[:4]))

    logWrite("\n\nPassword hash sent:\nHash = " + str(hex(save))[:128] + "\nSalt = " + str(salt))
    return (str(hex(save))[:128] + "," +str(salt))

#------------------------Sending and Reciving data-----------------------
def sendFile():
    placeHold = Tk()
    placeHold.withdraw()
    filePath = filedialog.askopenfilename()
    file = open("%s" %filePath, "rb")
    bite = file.read(200)
    while bite:
        sendData(str(bite), "File")
        bite = file.read(200)
    else:
        sendData("", "End")

    logWrite("File at " + str(filePath) + "sent to server")

    placeHold.destroy()


def sendData(toSend, command = "None"):
    #------------------------Hamming Code-----------------------
    inputRaw = [str(bin(ord(x))) for x in toSend]
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
    #------------------------RSA Encryption-----------------------
    inputRaw = re.findall("............", inputRaw)
    dataIn = ""
    for i in inputRaw:
        dataIn += chr(int(i,2))

    dataInList = list(dataIn)

    pubKey = 4363*2539
    sharedKey = 17
    encry = []

    privateKey = 651221
    for m in dataInList:
        message = ord(m)
        encry.append(hex(powMod(message, sharedKey, pubKey)))

    encry = "".join(encry)
    if command != "File" or command != "End":
        logWrite("\n\nData sent to server:\n" + str(encry))
    #------------------------Final Data Send-----------------------
    finalMessage = encry + commServer + command + endMess
    print(len(finalMessage))
    sock.send(finalMessage.encode())

def decodeData(toDecode):
    #------------------------Formating-----------------------
    toDecode = toDecode.replace(toDecode[toDecode.index(commServer):], "")
    #------------------------Decryption-----------------------
    pubKey = 4363*2539
    sharedKey = 17

    privateKey = 651221
    toDecode = toDecode.split("0x")[1:]

    errorCheck = []
    for c in toDecode:
        errorCheck.append(chr(powMod(int(c,16), privateKey, pubKey)))

    errorCheck = "".join(errorCheck)

    #------------------------Parity Checker-----------------------
    errorCheck = "".join([parityFix(bin(ord(x))) for x in errorCheck]).replace("b","")
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
    inputRaw = re.findall("............", errorCheck)
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

    output = ""
    inputRaw = "".join(inputRaw)
    inputRaw = inputRaw.replace("%", "")
    inputRaw = re.findall("........", inputRaw)
    for i in [int(x,2) for x in inputRaw]:
        output += chr(i)

    return output

#------------------------Processing-----------------------
##rootWindow.mainloop()

data = sock.recv(2048)
print(data.decode())
##sendData("Edward,"+str(IP)+","+str(hashPassword("1234")), "Register")
sendFile()
sendData("", "Close")
