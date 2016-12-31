import socket, sys, re, math, sqlite3, string, random, os, csv
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
    toSend = ""
    for i in dataBaseGetAllClientsSafe():
        toSend += str(i) + ","
    if len(toSend) == 0:
        toSend = "NONE REGISTERED"
    conn.send(str(toSend).encode())
    message = ""
    login = 0
    user = ""
    while 1:
        data = conn.recv(8192)
        message = data.decode()
        command = message[message.index(commServer)+7:].replace(endMess,"")
        allUsers = dataBaseGetAllClients()
        if command == "Password":
            #Values 0: username, 1: ip, 2: hash, 3: salt
            values = decodeData(message).split(",")
            if values[0] in [x[0] for x in allUsers]:
                if values[2] == allUsers[[x[0] for x in allUsers].index(values[0])][1]:
                    conn.send("Login sucessful!".encode())
                    user = values[0]
                    conn.send("CLEAR".encode())
                else:
                    print("Login Failed",allUsers[[x[0] for x in allUsers].index(values[0])][1])
                    conn.send("ERROR".encode())

        elif command == "Register":
            values = decodeData(message).split(",")
            if values[0] in [x[0] for x in allUsers]:
                conn.send("ERROR".encode())
                conn.close()
            else:
                conn.send("CLEAR".encode())
                dataBaseRegister(values[0], values[2], values[3], 111)# 111 is placeholder
                user = values[0]

                conn.send("Registered sucessful!".encode())

        elif command == "File":
            file = message.replace(message[message.index(commServer):], "")

            while command == "File":
                data = conn.recv(8192)
                message = data.decode()
                command = message[message.index(commServer)+7:].replace(endMess,"")
                file += message.replace(message[message.index(commServer):], "")
            else:
                file += message.replace(message[message.index(commServer):], "")
                dataUpdate(dataAddDirectory(user, values[2], "toSend", ".txt"), file)# toSend and txt are placeholders
                file = ""

        elif command == "Ping":
            pass
        elif command == "Close":
            break

    conn.close()

def isPrime(toTest):

    divisblity = toTest - 1
    count = 0
    while divisblity % 2 == 0:
        divisblity = divisblity // 2
        count += 1

    for trials in range(5):
        a = random.randint(2, toTest - 1)
        v = pow(a, divisblity, toTest)
        if v != 1:
            iteration = 0
            while v != (toTest - 1):
                if iteration == count:
                    return False
                else:
                    iteration += 1
                    v = (v ** 2) % toTest
    return True

def eGCD(e, n):
    x, y, a, b = 1,0,0,1
    count = 0
    while n and count < 10000:
        q = e//n

        x, y = y, x - q*y

        e, n = n, e - q*n
        count+=1
    return(e,x,a)

def keyGen():
    factorOne = 4
    while not isPrime(factorOne):
        factorOne = random.randint(2**32,2**48)


    factorTwo = 4
    while not isPrime(factorTwo):
        factorTwo = random.randint(2**32, 2**48)


    semi = factorOne*factorTwo
    print("Semiprime", semi)

    totient = (factorOne - 1) * (factorTwo - 1)

    sharedKey = 2
    while 1:
        privateKey = eGCD(sharedKey, totient)

        if privateKey[1] > 1 and privateKey[1] == abs(privateKey[1]) and isPrime(sharedKey):
            break
        else:
            sharedKey += 1

    factorOne = 0#--------Clear factors from RAM-------
    factorTwo = 0

    print("Shared key:", sharedKey)
    print("Private key:", privateKey[1])
    return semi, sharedKey, privateKey[1]


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
#------------------------Database commands-----------------------
def dataBaseRepair():
    dataBase = sqlite3.connect("serverDatabase.db")

    dataBase.execute('''CREATE TABLE clients
                 (user varchar(20), password varchar(128), salt varchar(16),publicKey INTEGER,
                 PRIMARY KEY(user, password))''')

    dataBase.execute('''CREATE TABLE linkClientsData
                 (user varchar(20), password varchar(128), dataID INTEGER, permisson INTEGER,
                 FOREIGN KEY (user, password) REFERENCES clients(user, password),
                 FOREIGN KEY (dataID) REFERENCES data(dataID))''')

    dataBase.execute('''CREATE TABLE data
                 (dataID INTEGER PRIMARY KEY, fileName varchar(128), directory varchar(128), fileType varchar(16))''')

    dataBase.close()

def dataBaseRegister(user,password,salt, publicKey):
    dataBase = sqlite3.connect("serverDatabase.db")

    dataBase.execute("INSERT INTO clients(user, password, salt, publicKey) VALUES (?,?,?,?)", (user, password, salt, publicKey))
    dataBase.commit()

    dataBase.close()


def dataBaseGetAllClients():
    dataBase = sqlite3.connect("serverDatabase.db")

    toReturn = dataBase.execute("SELECT * FROM clients").fetchall()
    dataBase.close()
    return toReturn

def dataBaseGetAllClientsSafe():
    dataBase = sqlite3.connect("serverDatabase.db")

    toReturn = dataBase.execute("SELECT user, salt FROM clients").fetchall()
    dataBase.close()
    return toReturn

def dataAddDirectory(user, password, fileName, fileType):
    dataBase = sqlite3.connect("serverDatabase.db")
    chars = string.ascii_letters + string.digits
    fileLocation = "".join(random.choice(chars) for i in range(10)) + ".txt"
    directory = 'dataStore/%s' %fileLocation

    dataBase.execute("INSERT INTO data(fileName, directory, fileType) VALUES (?,?,?)", (fileName, directory, fileType))
    dataBase.commit()
    dataID = dataBase.execute("SELECT dataID FROM data WHERE directory = ?", ('dataStore/%s' %fileLocation,)).fetchall()[0][0]
    print(dataID)
    dataBase.execute("INSERT INTO linkClientsData VALUES (?,?,?,?)", (user, password, dataID, 1))
    dataBase.commit()

    dataBase.close()
    return fileLocation

def dataUpdate(fileLocation, data):
    currentDir = os.path.dirname(os.path.realpath('__file__'))
    dataFile = open(os.path.join(currentDir, 'dataStore/%s' %(fileLocation)),"a")
    dataFile.write(data)
    dataFile.close()

def dataBaseGetAllFiles(user, password):
    dataBase = sqlite3.connect("serverDatabase.db")

    dataList = dataBase.execute("SELECT dataID FROM linkClientsData WHERE user = ? AND password = ?", (user, password)).fetchall()
    print(dataList)
    toReturn = []
    for x in dataList:
        y = dataBase.execute("SELECT fileName FROM data WHERE dataID = ?", (x[0],)).fetchall()[0][0]
        toReturn.append(y)
    dataBase.close()
    return toReturn

def dataBaseRetriveFile(user, password, fileName):
    dataBase = sqlite3.connect("serverDatabase.db")
    fileLocation = ""

    dataList = dataBase.execute("SELECT dataID FROM linkClientsData WHERE user = ? AND password = ?", (user, password)).fetchall()
    print(dataList)
    toReturn = []
    for x in dataList:
        y = dataBase.execute("SELECT directory FROM data WHERE dataID = ? AND fileName = ?", (x[0],fileName)).fetchall()
        if y:
            fileLocation = y[0][0]
            break;

    currentDir = os.path.dirname(os.path.realpath('__file__'))
    dataFile = open(os.path.join(currentDir, '%s' %(fileLocation)),"r+")
    return dataFile


#------------------------Sending and Reciving data-----------------------
def sendFile(file):
    bite = file.read(200)
    while bite:
        sendData(str(bite), "File")
        bite = file.read(200)
    else:
        sendData("", "End")

    file.close()

##    logWrite("File at " + str(filePath) + "sent to server")


def sendData(toSend, command):
    #------------------------Hamming Code-----------------------
    inputRaw = [str(bin(ord(x))) for x in toSend]
    for x in inputRaw:
        if len(x) == 8:
            y = "0" + x
            inputRaw[inputRaw.index(x)] = y

    inputRaw = "".join(inputRaw)
    inputRaw = inputRaw.replace("b", "")

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
#------------------------Start-up and repair--------------
if not(os.path.isfile("serverDatabase.db")):
    dataBaseRepair()

if not(os.path.isfile("RSAKeys.csv")):
    semi, sharedKey, privateKey = keyGen()
    keyFile = open("RSAKeys.csv", "w", newline= '')
    fileWriter = csv.writer(keyFile)
    fileWriter.writerows((str(semi),str(sharedKey),str(privateKey)))
    keyFile.close()

keyFile = open("RSAKeys.csv", "r")
keyData = keyFile.read().replace(",","").split("\n")
semi = int(keyData[0])
sharedKey = int(keyData[1])
privateKey = int(keyData[2])
keyFile.close()
#------------------------Processing-----------------------
while 1:
    conn, addr = s.accept()
    print("Connected to:" + addr[0] + ":" + str(addr[1]))

    start_new_thread(threadedClient, (conn,))
