import math, re, random, string, socket
#------------------------Initialization-----------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "192.168.0.10"
port = 5555
sock.connect((server,port))

commServer = "COMMAND"
endMess = "EOFEOFEOFX"

def logWrite(toWrite):
    #------------------------Data Logging-----------------------
    log = open("logFile.txt", "a")
    log.write(toWrite)
    log.close()

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

    logWrite("\n\nPassword hash sent:\nHash = " + str(hex(save))[:256] + "\nSalt = " + str(salt))
    sendData(str(hex(save))[:128] + "\n" + str(salt), "Password")


def sendData(toSend, command):
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
        encry.append(hex((message**sharedKey)%pubKey))

    encry = "".join(encry)
    logWrite("\n\nData sent to server:\n" + str(encry))
    #------------------------Final Data Send-----------------------
    finalMessage = encry + commServer + command + endMess
    print(finalMessage)
    sock.send(finalMessage.encode())
#------------------------Processing-----------------------
hashPassword("hello")
