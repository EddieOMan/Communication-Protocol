import socket, sys, re, math, sqlite3
from _thread import *

host = ''
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

commServer = "COMMAND"
endMess = "EOFEOFEOFX"

try:
    s.bind((host,port))
except socket.error as e:
    print(str(e))

s.listen(5)
print("Waiting for connection...")
def threadedClient(conn):
    conn.send(str.encode("Welcome, type your name:\n"))
    message = ""
    while 1:
        data = conn.recv(2048)
        message = data.decode()
        command = message[message.index(commServer)+7:].replace(endMess,"")
        if command == "Password":
            print(decodeData(message))
        elif "ConnectTo" in command:
            pass
        elif command == "Ping":
            pass

    conn.close()

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
#------------------------Database commands-----------------------
def dataBaseRepair():
    dataBase = sqlite3.connect("serverDatabase.db")

    dataBase.execute('''CREATE TABLE clients
                 (user text, online boolean, IP interger, password text, salt text)''')

    dataBase.close()

def dataBaseInsert(values):
    dataBase = sqlite3.connect("serverDatabase.db")

    dataBase.execute("INSERT INTO clients VALUES (?,?,?,?,?)", values)
    dataBase.commit()

    dataBase.close()

#------------------------Sending and Reciving data-----------------------
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

def decodeData(toDecode):
    #------------------------Formating-----------------------
    toDecode = toDecode.replace(toDecode[toDecode.index(commServer):], "")
    print(toDecode)
    #------------------------Decryption-----------------------
    pubKey = 4363*2539
    sharedKey = 17

    privateKey = 651221
    toDecode = toDecode.split("0x")[1:]

    errorCheck = []
    for c in toDecode:
        errorCheck.append(chr(powMod(int(c,16), privateKey, pubKey)))

    errorCheck = "".join(errorCheck)
    print(errorCheck)

    #------------------------Parity Checker-----------------------
    errorCheck = "".join([parityFix(bin(ord(x))) for x in errorCheck]).replace("b","")
    print(len(errorCheck))
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
    print(inputRaw)
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
    print(inputRaw)
    inputRaw = re.findall("........", inputRaw)
    for i in [int(x,2) for x in inputRaw]:
        output += chr(i)

    return output

while 1:
    conn, addr = s.accept()
    print("Connected to:" + addr[0] + ":" + str(addr[1]))

    start_new_thread(threadedClient, (conn,))
