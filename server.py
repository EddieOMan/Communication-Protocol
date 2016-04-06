import socket, sys
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
        if message[message.index(commServer)+7:].replace(endMess,"") == "Password":
            print("Password recived")

    conn.close()

while 1:
    conn, addr = s.accept()
    print("Connected to:" + addr[0] + ":" + str(addr[1]))

    start_new_thread(threadedClient, (conn,))
