#---------------------initalization-------------
import socket, re, math, sqlite3, string, random, os, csv
from _thread import *#Imports all functions mentioned in design section

host = ''#This indicates the host of the connection is the current computer
port = 5555#This is the allocated port number for the algorithm

#This creates the socket for the connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Predefined key word for the protocol trasmission
commServer = "COMMAND"
endMess = "EOFEOFEOFX"

#Binds the host of the connection to the socket
try:
    s.bind((host,port))
except socket.error as e:
    print(str(e))
    #This can fail somtimes so exception is needed

s.listen(5)
print("Waiting for connection...")

#---------------- Main loop for program----------------
def threadedClient(conn):
    toSend = ""
    #Retrieves all the registered users as well as their salts for hashing
    for i in dataBaseGetAllClientsSafe():
        toSend += str(i) + ","
    if len(toSend) == 0:
        #If no users are registered then a message indicating this is sent
        toSend = "NONE REGISTERED"

    #Sends the servers public IP address to the clinet connected
    conn.send(str(semi).encode())

    #Gets the public key sent by the client and saves it as a global variable
    global publicKey
    publicKey = int(conn.recv(128).decode())
    print(publicKey)

    #Sends the users and salts
    conn.send(str(toSend).encode())

    message = ""
    login = 0
    user = ""

    while 1:
        #The loop constantly checks for the client that is currently connected to send a request
        data = conn.recv(32768)

        message = data.decode()
        try:
            #This takes the message sent by the client and finds the command then stores it as a variable
            command = message[message.index(commServer)+7:].replace(endMess,"")
        except:
            print(len(message))

        #Gets all users and information from the client table in the database
        allUsers = dataBaseGetAllClients()

        if command == "Password":
            #Values 0: username, 1: ip, 2: hash, 3: salt 4: public key
            values = decodeData(message.replace(message[message.index(commServer):], "")).split(",")
            #Gets the values submitted by the user
            if values[0] in [x[0] for x in allUsers]:
                #Checks that the client is a registed user and has the correct has for the password
                if values[2] == allUsers[[x[0] for x in allUsers].index(values[0])][1]:
                    user = values[0]
                    password = values[2]
                    conn.send("CLEAR".encode())
                    #If the hashed password is correct then a message indicating this is returned
                else:
                    #If the password is wrong an error is returned
                    print("Login Failed",allUsers[[x[0] for x in allUsers].index(values[0])][1])
                    conn.send("ERROR".encode())

        elif command == "Register":
            #The register command allows users to have their data to be sent to the database
            values = decodeData(message.replace(message[message.index(commServer):], "")).split(",")
            #If the username is already registered an error is returned
            if values[0] in [x[0] for x in allUsers]:
                conn.send("ERROR".encode())
                conn.close()

            else:
                #Otherwise a clear message is sent
                conn.send("CLEAR".encode())
                dataBaseRegister(values[0], values[2], values[3], values[4])
                user = values[0]
                password = values[2]

        elif command == "File":
            #The file command indicates the client is sending a file
            file = message.replace(message[message.index(commServer):], "")

            while command == "File":
                #The file procedure runs until the file is fully sent then the file is reconstructed
                data = conn.recv(32768)
                message = data.decode()
                command = message[message.index(commServer)+7:].replace(endMess,"")
                file += message.replace(message[message.index(commServer):], "")
                print(len(message))
            else:
                #The name of the file is saved in the database with the file type
                fileName = decodeData(message.replace(message[message.index(commServer):], ""))

                fileInformation = dataAddDirectory(user, password, fileName.split(".")[0], fileName.split(".")[1])

                dataUpdate(fileInformation[0], file)
                print(fileName.split(".")[2])

                #The permissions sent by the client for other users to acess the file are inserted into the database

                for x in fileName.split(".")[2].split(","):
                    #Permissions of 1 priorty
                    dataBaseAddPermission(x, fileInformation[1], 1)

                for y in fileName.split(".")[3].split(","):
                    #Permissions of 2 priorty
                    dataBaseAddPermission(y, fileInformation[1], 2)

                file = ""#The file is then clear for later usage

        elif command == "Get":
            #Returns all files under the username of the client
            conn.send(str(dataBaseGetAllFiles(user, password)).encode())

        elif command == "Delete":
            #Will check the proirty of the user then delete the file if appopriate
            values = decodeData(message.replace(message[message.index(commServer):], "")).split(",")
            fileName = values[0]
            print("Deleting ", fileName)
            try:
                #A try except is necessary because it can cause a crash if the file is not found
                fileToDeleteDir = dataBaseRetriveFile(user, password, fileName)[1]

                #The complete variable store if the user has permission to delete the file
                #Also deletes all other permissions that have this file linked in them
                complete = dataBaseDeleteRecord(user, password, fileName)

                if complete ==  "CLEAR":
                    #Deletes the file from the dataStore folder
                    os.remove(fileToDeleteDir)
                    print("CLEAR File ", fileName, " deleted")

                else:
                    print("User does not have permission to delete this file")

            except:
                print("ERROR no file of name: ", fileName, " found")

        elif command == "Send":
            try:
                #The send command takes the file requested and returns a copy to the user
                values = decodeData(message.replace(message[message.index(commServer):], "")).split(",")
                fileName = values[0]

                fileToSend = dataBaseRetriveFile(user, password, fileName)[0]
                rawFile = decodeData(fileToSend.read())
                count = 0

                #Splits the file into packets for transmission
                bite = rawFile[count*200:(count+1) * 200]

                while bite:
                    sendData(str(bite), "File")
                    count += 1
                    bite = rawFile[count*200:(count+1) * 200]
                else:
                    sendData("", "End")
                fileToSend.close()
            except:
                print("ERROR no file of name: ", fileName, " found")

        elif command == "Close":
            break

    conn.close()

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

def keyGen():
    factorOne = 4

    #Generate two random prime numbers between 2^32 and 2^48
    while not isPrime(factorOne):
        factorOne = random.randint(2**32,2**48)


    factorTwo = 4
    while not isPrime(factorTwo):
        factorTwo = random.randint(2**32, 2**48)

    #Creates the public key of the server
    semi = factorOne*factorTwo
    print("Semiprime", semi)

    totient = (factorOne - 1) * (factorTwo - 1)

    #This forces the shared key to be 17 as is important for proper encryption
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

    return semi, sharedKey, privateKey[1]

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
#------------------------Database commands-----------------------
def dataBaseRepair():
    #Runs if no database is detected
    dataBase = sqlite3.connect("serverDatabase.db")#Connects to the database server/the file is created if it does not exsist

    #Creates the client table with details specified in documentation
    dataBase.execute('''CREATE TABLE clients
                 (user varchar(20), password varchar(128), salt varchar(16),publicKey varchar(128),
                 PRIMARY KEY(user, password))''')

    #Creates the link table with details specified in documentation
    dataBase.execute('''CREATE TABLE linkClientsData
                 (user varchar(20), password varchar(128), dataID INTEGER, permission INTEGER,
                 FOREIGN KEY (user, password) REFERENCES clients(user, password),
                 FOREIGN KEY (dataID) REFERENCES data(dataID))''')

    #Creates the data/file table with details specified in documentation
    dataBase.execute('''CREATE TABLE data
                 (dataID INTEGER PRIMARY KEY, fileName varchar(128), directory varchar(128), fileType varchar(16))''')

    #Saves any changes to file inserted data must also be commited
    dataBase.close()

def dataBaseRegister(user,password,salt, publicKey):
    dataBase = sqlite3.connect("serverDatabase.db")
    #Adds user data to database in a form that disallows sql injection

    dataBase.execute("INSERT INTO clients(user, password, salt, publicKey) VALUES (?,?,?,?)", (user, password, salt, publicKey))
    dataBase.commit()

    dataBase.close()


def dataBaseGetAllClients():
    dataBase = sqlite3.connect("serverDatabase.db")
    #Returns all information about users (this should not be sent to the client)

    toReturn = dataBase.execute("SELECT * FROM clients").fetchall()
    dataBase.close()
    return toReturn

def dataBaseGetAllClientsSafe():
    dataBase = sqlite3.connect("serverDatabase.db")
    #Returns all information about users that does not compromise security

    toReturn = dataBase.execute("SELECT user, salt FROM clients").fetchall()
    dataBase.close()
    return toReturn

def dataAddDirectory(user, password, fileName, fileType):
    dataBase = sqlite3.connect("serverDatabase.db")

    #Creates a directory using random characters and digits
    chars = string.ascii_letters + string.digits
    fileLocation = "".join(random.choice(chars) for i in range(10)) + ".txt"

    #The folder for datastore has the random file name appened
    directory = 'dataStore/%s' %fileLocation

    #Creates a link in the data base of the place the raw data of that file is stored
    dataBase.execute("INSERT INTO data(fileName, directory, fileType) VALUES (?,?,?)", (fileName, directory, fileType))
    dataBase.commit()

    #Gets the primary key of the record just added
    dataID = dataBase.execute("SELECT dataID FROM data WHERE directory = ?", ('dataStore/%s' %fileLocation,)).fetchall()[0][0]
    print(dataID)

    #Creats a link between the client and data in the link table
    dataBase.execute("INSERT INTO linkClientsData VALUES (?,?,?,?)", (user, password, dataID, 1))
    dataBase.commit()

    dataBase.close()
    return fileLocation, dataID

def dataUpdate(fileLocation, data):
    #Inserts the information of the raw file into the storage location
    currentDir = os.path.dirname(os.path.realpath('__file__'))
    dataFile = open(os.path.join(currentDir, 'dataStore/%s' %(fileLocation)),"a")
    dataFile.write(data)
    dataFile.close()

def dataBaseGetAllFiles(user, password):
    #Finds all files asociated with the user as filenames to be sent to client
    dataBase = sqlite3.connect("serverDatabase.db")

    dataList = dataBase.execute("SELECT dataID FROM linkClientsData WHERE user = ? AND password = ?", (user, password)).fetchall()
    toReturn = []
    for x in dataList:
        y = dataBase.execute("SELECT fileName FROM data WHERE dataID = ?", (x[0],)).fetchall()[0][0]
        toReturn.append(y)
    dataBase.close()
    return toReturn

def dataBaseRetriveFile(user, password, fileName):
    #Returns the location and opens a specified copy of file to be sent to client
    dataBase = sqlite3.connect("serverDatabase.db")
    fileLocation = ""

    dataList = dataBase.execute("SELECT dataID FROM linkClientsData WHERE user = ? AND password = ?", (user, password)).fetchall()
    toReturn = []
    for x in dataList:
        y = dataBase.execute("SELECT directory FROM data WHERE dataID = ? AND fileName = ?", (x[0],fileName)).fetchall()
        if y:
            fileLocation = y[0][0]
            dataBase.close()
            break;

    currentDir = os.path.dirname(os.path.realpath('__file__'))#Gets the current file location
    dataFile = open(os.path.join(currentDir, '%s' %(fileLocation)),"r+")

    #Returns the opened file and file path
    return dataFile, os.path.join(currentDir, '%s' %(fileLocation))

def dataBaseDeleteRecord(user, password, fileName):
    dataBase = sqlite3.connect("serverDatabase.db")
    #Checks if the user hasa permission to delete the file and deletes the record if this is the case

    try:
        dataList = dataBase.execute("SELECT dataID FROM linkClientsData WHERE user = ? AND password = ? AND permission = 1", (user, password)).fetchall()
    except:
        #Returned if the user does not have permission
        return "ERROR"

    toReturn = []
    for x in dataList:
        y = dataBase.execute("SELECT directory FROM data WHERE dataID = ? AND fileName = ?", (x[0],fileName)).fetchall()
        if y:
            dataBase.execute("DELETE FROM data WHERE dataID = ? AND fileName = ?", (x[0],fileName))
            dataBase.execute("DELETE FROM linkClientsData WHERE dataID = ?", (x[0],))#This deletes all permission and records of the file in the database

            print(x[0], fileName)

            dataBase.commit()
            dataBase.close()
            return "CLEAR"#Returns to indicate the user has permission to delete the file

            break;


def dataBaseAddPermission(user, dataID, permission):
    #Adds all the permissions specified by the user
    dataBase = sqlite3.connect("serverDatabase.db")
    password = dataBase.execute("SELECT password FROM clients WHERE user = ?", (user,)).fetchall()

    #The try except checks if the user is registered in the database
    try:
        dataBase.execute("INSERT INTO linkClientsData VALUES (?,?,?,?)", (user, password[0][0], dataID, int(permission)))
    except:
        print("ERROR no users with this permission")

    dataBase.commit()
    dataBase.close()

#------------------------Sending and Reciving data-----------------------
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
    sharedKey = 17
    #Formats the input for later process
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

    #Turns the binary string into a set of 12 bit packets
    y = 0
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

        if location > 0:#Errors are alerted and auto corrected for the server
            response = "y"
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

    #Removes parity bits where placeholders are
    output = ""
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
    conn.send(finalMessage.encode())

def decodeData(toDecode):
    #Performs the inverse functions of the sendData function
    return inverseHamming(decrypt(toDecode))

#------------------------Start-up and repair--------------
if not(os.path.isfile("serverDatabase.db")):
    #Checks to find the database if it can then the database repair is run
    dataBaseRepair()

if not(os.path.isfile("RSAKeys.csv")):
    #Checks to find the RSAkeys stored in the comma seperated file
    #New keys are generated if the file is not found
    semi, sharedKey, privateKey = keyGen()

    keyFile = open("RSAKeys.csv", "w", newline= '')
    fileWriter = csv.writer(keyFile)
    fileWriter.writerows((str(semi),str(sharedKey),str(privateKey)))

    keyFile.close()#Closes connection to file for future usage

#Open the RSA key file to get the keys
keyFile = open("RSAKeys.csv", "r")
keyData = keyFile.read().replace(",","").split("\n")

#All RSA keys are decleared as global variables for usage in the encryption and decryption functions
global semi
semi = int(keyData[0])

global sharedKey
sharedKey = int(keyData[1])

global privateKey
privateKey = int(keyData[2])

keyFile.close()
#------------------------Processing-----------------------
while 1:
    #The program constantly loops to find a telnet conenction through the 5555 port on the network
    conn, addr = s.accept()
    print("Connected to:" + addr[0] + ":" + str(addr[1]))

    start_new_thread(threadedClient, (conn,))
