import math, re, random, string, socket, os, csv
from tkinter import *
from tkinter import filedialog
#------------------------Initialization-----------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "192.168.0.14"
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
            #a, b = b, a - q*b

        e, n = n, e - q*n
        count+=1
    return(e,x,a)

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
    file.close()
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
    logWrite("\n\nData sent to server:\n" + str(encry))
    #------------------------Final Data Send-----------------------
    finalMessage = encry + commServer + command + endMess
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

##def reciveFile():
##    if command == "File":
##        file = message.replace(message[message.index(commServer):], "")
##
##    while command == "File":
##        data = conn.recv(8192)
##        message = data.decode()
##        command = message[message.index(commServer)+7:].replace(endMess,"")
##        file += message.replace(message[message.index(commServer):], "")
##    else:
##        file += message.replace(message[message.index(commServer):], "")
##        return file

#------------------------Start-up and repair--------------
if not(os.path.isfile("RSAKeysClient.csv")):
    semi, sharedKey, privateKey = keyGen()
    keyFile = open("RSAKeysClient.csv", "w", newline= '')
    fileWriter = csv.writer(keyFile)
    fileWriter.writerows((str(semi),str(sharedKey),str(privateKey)))
    keyFile.close()

keyFile = open("RSAKeysClient.csv", "r")
keyData = keyFile.read().replace(",","").split("\n")
semi = keyData[0]
sharedKey = keyData[1]
privateKey = keyData[2]
keyFile.close()
print(semi, sharedKey, privateKey)

#------------------------Processing-----------------------
data = sock.recv(2048)
dataUsers = data.decode()
#------------------------Tkinter definitions-----------------------
rootWindow = Tk()
rootWindow.geometry("0x0")

#------------------------Window Parent Class-----------------------
class parentWindow(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self)
        self.parent = parent
        self.protocol("WM_DELETE_WINDOW", self.onClosing)

    def onClosing(self):
        rootWindow.destroy()
        sendData("", "Close")
        self.destroy()

    def openWindow(self, window=""):
        if window == "Login":
            chLoginWindow(self.parent)
            self.destroy()
        elif window == "Start":
            chStartWindow(self.parent)
            self.destroy()
        elif window == "Main":
            self.parent.frame.deiconify()
            self.destroy()
        elif window == "Register":
            chRegisWindow(self.parent)
            self.destroy()

#------------------------Window SubClasses-----------------------
class chStartWindow(parentWindow):
    def __init__(self, parent):
        parentWindow.__init__(self, parent)
        loginBut = Button(self, text = "Login", command=lambda:self.openWindow("Login"), font=("Helvetica", 18))
        loginBut.pack()
        regisBut = Button(self, text = "Register", command=lambda:self.openWindow("Register"), font=("Helvetica", 18))
        regisBut.pack()


class chLoginWindow(parentWindow):
    def __init__(self, parent):
        parentWindow.__init__(self, parent)
        Label(self, text = "Username:").place(x = 30, y = 30)
        entUser = Entry(self)
        entUser.place(x = 30, y = 50)
        Label(self, text = "Password:").place(x = 30, y = 70)
        entPassword = Entry(self)
        entPassword.place(x = 30, y = 90)
        Button(self, text = "Enter", command = lambda:self.passHash(entUser.get(), entPassword.get())).place(x = 45, y = 110)

    def passHash(self, user, password):
        listUsers = [x.split(",") for x in (dataUsers.replace("(","").replace("'","").split("),"))]
        for regiUser in listUsers:
            if user == regiUser[0]:
                print(regiUser[1][1:])
                sendData(str(user) + ","+str(IP)+","+str(hashPassword(password, regiUser[1][1:])), "Password")
                data = sock.recv(2048)
                if data.decode() == "CLEAR":
                    self.openWindow("Main")
                else:
                    print("Password incorrect")

class chRegisWindow(parentWindow):
    def __init__(self, parent):
        parentWindow.__init__(self, parent)
        Label(self, text = "Username:").place(x = 30, y = 30)
        entUser = Entry(self)
        entUser.place(x = 30, y = 50)
        Label(self, text = "Password:").place(x = 30, y = 70)
        entPassword = Entry(self)
        entPassword.place(x = 30, y = 90)
        Label(self, text = "Confirm Password:").place(x = 30, y = 110)
        entRePassword = Entry(self)
        entRePassword.place(x = 30, y = 130)
        Button(self, text = "Enter", command = lambda:self.passHash(entUser.get(), entPassword.get(), entRePassword.get())).place(x = 45, y = 150)

    def passHash(self, user, password, confPass):
##        self.openWindow("Main")
        if confPass != password:
            print("Confirm password diffrent to password")
        else:
            sendData(user+","+str(IP)+","+str(hashPassword(password)), "Register")
            if data.decode() == "CLEAR":
                    self.openWindow("Main")
            else:
                print("Password incorrect")


#------------------------mainWindow-----------------------
class mainWindow(object):
    def __init__(self, parent):
        self.root = parent
        self.root.title("Protocol")
        self.root.withdraw()
        self.frame = Toplevel(parent)
##        self.frame.geometry("1280x720")
        Button(self.frame, text = "Ping", command = lambda:self.ping()).place(x = 45, y = 15)
        Button(self.frame, text = "Send File", command = sendFile).place(x = 45, y = 45)
        Button(self.frame, text = "Delete File", command = lambda:self.ping()).place(x = 45, y = 75)
        entPermissions = Entry(self.frame)
        entPermissions.place(x = 45, y = 105)
        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.frame.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.openWindow()

    def hide(self):
        self.frame.withdraw()

    def openWindow(self, window=""):
        self.hide()
        if window == "Start" or window == "":
            chStartWindow(self)

    def ping(self):
        pass

    def onClosing(self):
        rootWindow.destroy()

#------------------------End-----------------------
mainWindow(rootWindow)

rootWindow.mainloop()
