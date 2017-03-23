import math, re, random, string, socket, os, csv, time#Imports all functions mentioned in design section
from tkinter import *
from tkinter import filedialog
#------------------------Initialization-----------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#Creates a socket for network connection
server = "192.168.0.11"#Server IP would be fixed in impelementation
port = 5555#Port for protocol
sock.connect((server,port))#Attempts to connect to server
IP = sock.getsockname()[0]#Prints current IP
print(IP)

#Predefined key word for the protocol trasmission
commServer = "COMMAND"
endMess = "EOFEOFEOFX"


def logWrite(toWrite):
    #------------------------Data Logging-----------------------
    #A procedure that write all important interations with the server in a log text file
    log = open("logFile.txt", "a")
    log.write(toWrite)
    log.close()

def powMod(x, y, z):
    #The power modulus function that works by reduction mentioned in documentation
    result = 1
    while y:
        if y % 2 == 1:
            result = result * x % z
        y >>= 1
        x = x * x % z
    return result

def parityFix(binInt):
    #Turns the binary integer into a 12 letter long string that is easier to iterate through
    binStr = str(binInt).replace("0b","")
    output = ""
    if len(binStr) < 12:
        for x in range(12-len(binStr)):
            output += "0"

    return output + binStr

def isPrime(toTest):
    #A function that checks if the input is prime

    divisblity = toTest - 1
    count = 0
    while divisblity % 2 == 0:
        divisblity = divisblity // 2
        count += 1

    for trials in range(5):
        #The more trials the more certain the answer will be if it is decleared prime

        a = random.randint(2, toTest - 1)#Generates a random number for the trial
        v = pow(a, divisblity, toTest)
        if v != 1:
            iteration = 0
            while v != (toTest - 1):
                if iteration == count:
                    return False
                else:
                    iteration += 1
                    v = (v ** 2) % toTest

    #If the number passes all trials then the number is likely a prime number
    return True

def eGCD(e, n):
    #The extended greatest common denominator function
    x, y, a, b = 1,0,0,1
    count = 0
    while n and count < 10000:
        q = e//n

        x, y = y, x - q*y

        e, n = n, e - q*n
        count+=1

    #The x value returns the private key to be used by the server
    return(e,x,a)

def placeHold(string, length):
    #Adds place holders to the hamming code function that is used in place of parity bits
    return string[:length] + "%" + string[length:]

def calcParity(string, pos):
    #Finds how many 1s are in a string and returns whether the parity bit for that position is 1 or 0
    parity = re.findall((''.join('.' for x in range(0,pos))+'?'),string[pos-1:])
    if parity == []:
        parity = string[pos-1:]

    else:
        #The for loop checks all bits in positions that apply to that current parity bit
        for x in range(1,len(parity)):
            if x % 2 != 0:
                parity[x] = ""

    parity ="".join(parity)
    if parity.count("1") % 2 == 0:
        return "0"
    else:
        return "1"

def keyGen():

     #Generate two random prime numbers between 2^32 and 2^48
    factorOne = 4
    while not isPrime(factorOne):
        factorOne = random.randint(2**32,2**48)


    factorTwo = 4
    while not isPrime(factorTwo):
        factorTwo = random.randint(2**32, 2**48)

    #Creates the public key of the client
    semi = factorOne*factorTwo
    print("Semiprime", semi)

    totient = (factorOne - 1) * (factorTwo - 1)

    #This forces the shared key to be 17 as is important for proper encryption the same as the server
    sharedKey = 17
    while 1:
        #Gets a private key from the eGCD function above
        privateKey = eGCD(sharedKey, totient)

        if privateKey[1] > 1 and privateKey[1] == abs(privateKey[1]) and isPrime(sharedKey):
            break
        else:
            #If the private key does not met the requirements for the RSA encryption another one is generated

            return keyGen()#An example of recurrsion

    factorOne = 0#--------Clear factors from RAM-------
    factorTwo = 0

    print("Shared key:", sharedKey)
    print("Private key:", privateKey[1])
    return semi, sharedKey, privateKey[1]



def hashPassword(password, salt = ""):
    #------------------------Hashing-----------------------

    if salt == "":
        #A random salt is generated if no salt is given
        chars = string.ascii_letters + string.digits
        salt = "".join(random.choice(chars) for i in range(16))

    #Turns the user intput into a number based on utf-8 values
    toHash = int("".join([str((ord(x))) for x in list(password+salt)]))
    parity = 473#Parity can be any number (better if it is somewhat small)

    for x in list(str(toHash)):
        #The xor function is run on the input
        #No inverse function for the xor operator exsist as the data become ambigious
        parity ^= int(x)<<3

    #Bitwise shift operator makes the hash hard to reverse without knowledge of original input
    save = (toHash ** parity>>int(str(toHash)[:4]))

    #The salt is save to the log file
    logWrite("Salt = " + str(salt))
    return (str(hex(save))[:128] + "," +str(salt))

def checkParity(string, pos):
    #Checks the parity of the parity bits with the string given then returns the position
    #of the bit if it is incorrect

    #Adds place holders
    endCheck = string[pos-1]
    string = list(string)
    string[pos-1] = "%"
    string = "".join(string)

    #Splits the string into a iteratable form that can then have the parity be calculated
    parity = re.findall((''.join('.' for x in range(0,pos))+'?'),(string[pos-1:]))
    if parity == []:
        parity = string[pos-1:]
    else:
        for x in range(1,len(parity)):
            if x % 2 != 0:
                parity[x] = ""

    parity ="".join(parity)
    #Calculates parity based on number of 1s found
    if parity.count("1") % 2 == int(endCheck):
        return 0
    else:
        return pos

#------------------------Sending and Reciving data-----------------------
def sendFile(permissions1, permissions2):
    #Splits the file into packet for transmission the packets take from the file are 200 hex or character long (depending on file type)
    placeHold = Tk()
    placeHold.withdraw()

    #Asks client for the file location with a pop-up menu
    filePath = filedialog.askopenfilename()
    file = open("%s" %filePath, "rb")
    bite = str(file.read(200))

    while bite:
        #Continues to iterate through the file until all of it has be sent
        cont = sendData(str(bite), "File")
        bite = file.read(200)

    else:
        #Adds the permission to the end of the file and file type seperated with a "."
        finalSendFile = os.path.basename(filePath) + "." + permissions1 + "." + permissions2
        sendData(finalSendFile, "End")
        print(os.path.basename(filePath))

    file.close()
    logWrite("\nFile at " + str(filePath) + "sent to server")

    placeHold.destroy()

def encrypt(inputRaw):
    #The main encryption RSA algorithm
    #The input is split into regulated sections

    inputRaw = re.findall("............", inputRaw)
    dataIn = ""

    #All the binary is turned into ascii
    for i in inputRaw:
        dataIn += chr(int(i,2))

    #The characters are put into a list
    dataInList = list(dataIn)

    sharedKey = 17#The shared key is always the same across the client server connection
    encry = []

    for m in dataInList:
        message = ord(m)
        #The main mathematics in the RSA algorithm using the power modulus reduction algorithm
        encry.append(hex(powMod(message,sharedKey,publicKey)))

    encry = "".join(encry)
    return encry

def hammingcode(toSend):
    #Turns the input string into a pure binary string equivelent to it using utf-8 encoding
    inputRaw = [str(bin(ord(x))) for x in toSend]

    for x in inputRaw:
        if len(x) == 8:
            #Formats the binary string for later processing
            #Formats so all the strings are of the same size
            y = "0" + x
            inputRaw[inputRaw.index(x)] = y

    inputRaw = "".join(inputRaw)
    inputRaw = inputRaw.replace("b", "")

    #Splits the string into sections of 8 bits
    inputRaw = re.findall("........", inputRaw)
    for y in inputRaw:
        i = y
        #Finds how many times to test for parity bits
        iterate =  math.ceil(math.log(len(i),2))+1

        for x in range(0, iterate):
            #Adds placeholders for the parity bits to be added later
            i = placeHold(i, (2**x)-1)

        iterate =  math.ceil(math.log(len(i),2))

        for x in range(0, iterate):
            #Calculates the parity of all individual parity bits in the binary string
            toAdd = calcParity(i,(2**x))
            i = list(i)
            i[(2**x)-1] = toAdd
            i = "".join(i)

        inputRaw[inputRaw.index(y)] = i

    inputRaw = "".join(inputRaw)

    #Returns the pairty bits
    return inputRaw

def decrypt(toDecode):
#------------------------Decryption-----------------------
    #Formats the input for later process
    sharedKey = 17

    toDecode = toDecode.split("0x")[1:]

    errorCheck = []

    #Turns all the character from hex into denary numbers then uses the power modulos by reduction
    #to inverse all RSA encryption
    for c in toDecode:
        errorCheck.append(chr(powMod(int(c,16), privateKey, semi)))

    #Returns the output as a string of ascii characters
    errorCheck = "".join(errorCheck)
    return errorCheck

def inverseHamming(errorCheck):
    #Takes a set of ascii characters then formats for processing
    errorCheck = "".join([parityFix(bin(ord(x))) for x in errorCheck]).replace("b","")

    y = 0
    #Turns the binary string into a set of 12 bit packets
    inputRaw = re.findall("............", errorCheck)
    for i in inputRaw:
        #Runs the hamming code and compares to the exsisting bits to check for errors
        iterate =  math.ceil(math.log(len(i),2))
        errors = []

        for x in range(0,iterate):
            result = checkParity(i,(2**x))
            errors.append(result)

        location = 0
        for x in errors:
            if x > 0:
                location += int(x)

        if location > 0:#Errors are alerted and prompt the client to ask if they want them restoted (if possible)
            response = input("Error in transmition detected, location at byte " + str(y) + "and bit" + str(location) + ".\nShould the program try to auto correct? y/n")
            if response.lower() == "y":
                #Changes damaged bits
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

    #Removes parity bits where placeholders are
    inputRaw = "".join(inputRaw)
    inputRaw = inputRaw.replace("%", "")
    inputRaw = re.findall("........", inputRaw)

    #Returns output as a string of utf-8 characters
    for i in [int(x,2) for x in inputRaw]:
        output += chr(i)

    return output

def sendData(toSend, command):
    #Performs the hamming and encryption on the message
    encry = encrypt(hammingcode(toSend))
    #------------------------Final Data Send-----------------------
    #The command and other formating are added to the end of the encrypted message
    finalMessage = encry + commServer + command + endMess
    sock.send(finalMessage.encode())

def decodeData(toDecode):
    #------------------------Formating-----------------------
    #Performs the inverse functions of the sendData function
    return inverseHamming(decrypt(toDecode))


#------------------------Start-up and repair--------------
if not(os.path.isfile("RSAKeysClient.csv")):
    #Checks to find the RSAkeys stored in the comma seperated file
    #New keys are generated if the file is not found
    semi, sharedKey, privateKey = keyGen()

    keyFile = open("RSAKeysClient.csv", "w", newline= '')

    fileWriter = csv.writer(keyFile)
    fileWriter.writerows((str(semi),str(sharedKey),str(privateKey)))

    keyFile.close()#Closes connection to file for future usage

keyFile = open("RSAKeysClient.csv", "r")#Open the RSA key file to get the keys
keyData = keyFile.read().replace(",","").split("\n")


#All RSA keys are decleared as global variables for usage in the encryption and decryption functions
global semi
semi = int(keyData[0])

global sharedKey
sharedKey = int(keyData[1])

global privateKey
privateKey = int(keyData[2])

keyFile.close()
print(semi, sharedKey, privateKey)

#------------------------Processing-----------------------
while 1:
    #The while loop tries to get a connection to send to the server of the client public key
    try:
        data = sock.recv(2048)

        sock.send(str(semi).encode())

        #The public key recived by the client is stored as a global public key for encryption
        global publicKey
        publicKey = int(data.decode())
        print(publicKey)
        break

    except:
        print("Failed connection re-trying:", data.decode())

data = sock.recv(2048)
dataUsers = data.decode()

#------------------------Tkinter definitions-----------------------
rootWindow = Tk()
rootWindow.geometry("0x0")

#------------------------Window Parent Class-----------------------
class parentWindow(Toplevel):
    #Acts as a template that the other windows inherit from
    def __init__(self, parent):
        Toplevel.__init__(self)
        self.parent = parent
        self.protocol("WM_DELETE_WINDOW", self.onClosing)

    def onClosing(self):
        #Tries to send a message to the server that the client has ended the connection
        #While also destroying any
        rootWindow.destroy()
        sendData("", "Close")
        self.destroy()

    def openWindow(self, window=""):
        #Changes the current window that the user is in depending on their input
        #Whilst destroying the copy of itself
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
    #Defines the first window that occurs when the program is run
    #With two buttons for login and register
    def __init__(self, parent):
        parentWindow.__init__(self, parent)
        loginBut = Button(self, text = "Login", command=lambda:self.openWindow("Login"), font=("Helvetica", 18))
        loginBut.pack()

        regisBut = Button(self, text = "Register", command=lambda:self.openWindow("Register"), font=("Helvetica", 18))
        regisBut.pack()


class chLoginWindow(parentWindow):
    #Defines the window for the user trying to login to the server with two entries and a button
    def __init__(self, parent):
        parentWindow.__init__(self, parent)
        Label(self, text = "Username:").place(x = 30, y = 30)

        entUser = Entry(self)
        entUser.place(x = 30, y = 50)

        Label(self, text = "Password:").place(x = 30, y = 70)

        entPassword = Entry(self)
        entPassword.place(x = 30, y = 90)

        #Runs the password hash function when the button is pressed with the information of the two entires
        Button(self, text = "Enter", command = lambda:self.passHash(entUser.get(), entPassword.get())).place(x = 45, y = 110)

    def passHash(self, user, password):
        #Password hashing algorithm
        #Checks to find the salt for the hashing algorithm and see if the user is register or not
        listUsers = [x.split(",") for x in (dataUsers.replace("(","").replace("'","").split("),"))]
        for regiUser in listUsers:
            if user == regiUser[0]:
                print(regiUser[1][1:])

                #Sends the users hashed password username IP and public key to the server with the command password
                sendData(str(user) + ","+str(IP)+","+str(hashPassword(password, regiUser[1][1:])) + "," + str(semi), "Password")

                #The program waits for a response from the server
                time.sleep(1)
                data = sock.recv(2048)
                print(data.decode())

                #If the hash is the same as what the server has the main window opens
                if data.decode() == "CLEAR":
                    self.openWindow("Main")
                else:
                    print("Password incorrect")

class chRegisWindow(parentWindow):
    #Design for register window 3 entries and one button
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
        #Runs the password hashing algorithm with additional checks for the register window
        #Checks the passwords entered are the same
        if confPass != password:
            print("Confirm password diffrent to password")
        else:
            #Sends all important data to server as above
            sendData(user+","+str(IP)+","+str(hashPassword(password)) + "," + str(semi), "Register")
            time.sleep(1)
            data = sock.recv(2048)
            if data.decode() == "CLEAR":
                    self.openWindow("Main")
            else:
                print("Password incorrect")


#------------------------mainWindow-----------------------
class mainWindow(object):
    #Main window design 4 buttons 3 entries
    def __init__(self, parent):
        self.root = parent
        self.root.title("Protocol")
        self.root.withdraw()
        self.frame = Toplevel(parent)

        #Defines size of window
        self.frame.geometry("400x350")

        #Button runs the send file command and take the two entries as input
        Button(self.frame, text = "Send File", command = lambda:sendFile(entPer1.get(), entPer2.get())).place(x = 45, y = 45)

        #Get file command request a string version of all avalible file names
        Button(self.frame, text = "Get Files", command = lambda:self.getFiles()).place(x = 45, y = 75)

        #Sends the server a delete command with the file name as input
        Button(self.frame, text = "Delete File", command = lambda:self.deleteFile(entDel.get())).place(x = 45, y = 105)

        #Sends the server a send command with the file name as inpu
        Button(self.frame, text = "Retrieve File", command = lambda:self.retrieveFile(entDel.get())).place(x = 45, y = 135)

        entDel = Entry(self.frame)
        entDel.place(x = 45, y = 165)

        Label(self.frame, text = "List permissions with priority 1(seperated with a comma)").place(x = 45, y = 195)

        entPer1 = Entry(self.frame)
        entPer1.place(x = 45, y = 225)

        Label(self.frame, text = "List permissions with priority 2(seperated with a comma)").place(x = 45, y = 255)

        entPer2 = Entry(self.frame)
        entPer2.place(x = 45, y = 285)

        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.frame.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.openWindow()

    def hide(self):
        self.frame.withdraw()

    def openWindow(self, window=""):
        self.hide()
        if window == "Start" or window == "":
            chStartWindow(self)

    def getFiles(self):
        #Sends get command to server
        sendData("","Get")
        time.sleep(1)

        data = sock.recv(2048)
        print(data.decode())

    def deleteFile(self, fileName):
        sendData(fileName +  ",", "Delete")

    def retrieveFile(self, fileName):
        sendData(fileName +  ",", "Send")

        data = sock.recv(8192)
        message = data.decode()

        command = message[message.index(commServer)+7:].replace(endMess,"")

        #File read in as packets then reconstructed through python built-in functions
        if command == "File":
            file = message.replace(message[message.index(commServer):], "")

        while command == "File":
            #Runs until the server stops sending the file reply
            data = sock.recv(8192)
            message = data.decode()

            command = message[message.index(commServer)+7:].replace(endMess,"")
            file += message.replace(message[message.index(commServer):], "")
        else:
            file += message.replace(message[message.index(commServer):], "")

        finalFile = decodeData(file)
        fileData = "".join("".join(finalFile.split("'b'")).split("'b\""))
        fileType = fileData.split(".")[-1]

        print(fileType,fileName)

        #Uses unicode escape codex to turn the code back into file data
        fileInput = "'".join(fileData.split("\'")[1:-1])
        fileInput = bytes(fileInput,"utf-8").decode("unicode_escape")

        #Writes file data to the file name taking information given by server
        toWrite = open("%s.%s"%(fileName,fileType), "w")
        toWrite.write(fileInput)
        toWrite.close()



    def onClosing(self):
        rootWindow.destroy()

#------------------------End-----------------------
#Runs the tkinter windows
mainWindow(rootWindow)

rootWindow.mainloop()
