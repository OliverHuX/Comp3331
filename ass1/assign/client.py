from socket import *
import os
import sys
import pickle
import threading
import time

auth = False
usernameVaild = False
connection = False
regist = False
SHT = False

def clientStart(host, port):
    global clientSocket
    global auth
    global usernameVaild
    global newmsg
    global connection
    global regist
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((host, port))
    connection = True
    regist = False
    newThread()
    while(1):
        time.sleep(0.5)
        if(not auth):
            if(not usernameVaild):
                if(regist):
                    print("Now registing")
                    password = (input("Enter a new password: "))
                    try:
                        clientSocket.send(password.encode())
                    except BrokenPipeError:
                        print("disconnection")
                        clientSocket.close()
                        sys.exit(0)
                else:
                    username = (input("Username: "))
                    try:
                        clientSocket.send(username.encode())
                    except BrokenPipeError:
                        print("disconnection")
                        clientSocket.close()
                        sys.exit(0)
            else:
                regist = False
                password = (input("Password: "))
                try:
                    clientSocket.send(password.encode())
                except BrokenPipeError:
                        print("disconnection")
                        clientSocket.close()
                        sys.exit(0)
        else:
            print(f"Enter one of the following commands: CRT, MSG, DLT, EDT, LST, RDT, UPD, DWN, RMV, XIT, SHT: ")
            msg = input()
            newmsg = msg.split()
            if(len(newmsg) == 3 and newmsg[0] == "UPD"):
                if(not os.path.exists(newmsg[2])):
                    print("FIle " + newmsg[2] + " does not exist")
                    continue
            try:
                clientSocket.send(msg.encode())
            except BrokenPipeError:
                print("disconnection")
                clientSocket.close()
                sys.exit(0)
            if(msg == "XIT"):
                time.sleep(0.5)
                clientSocket.close()
                break
            if(len(newmsg) == 2 and newmsg[0] == "SHT"):
                time.sleep(0.5)
                clientSocket.close()
                break
            if(SHT):
                clientSocket.close()
                sys.exit(0)

def receive():
    global auth
    global usernameVaild
    global connection
    global regist
    global SHT
    #global receivedMSG
    while(1):
        if(not auth):
            try:
                receivedMSG = clientSocket.recv(2048)
            except BrokenPipeError:
                print("disconnection")
                clientSocket.close()
                sys.exit(0)
            try:
                msg = pickle.loads(receivedMSG)[0]
                status = pickle.loads(receivedMSG)[1]
            except Exception:
                print("disconnection")
                sys.exit(0)
            if(not usernameVaild):
                if(regist):
                    auth = status
                    print(msg)
                if(not status and msg != "The user already logged in"):
                    regist = True
                    print(msg)
                elif(not status):
                    print(msg)
                usernameVaild = status
            else:
                print(msg)
                auth = status
                usernameVaild = status
        else:
            try:
                receivedMSG = clientSocket.recv(2048).decode()
            except BrokenPipeError:
                print("disconnection")
                clientSocket.close()
                sys.exit(0)
            if(receivedMSG == "UPDTrue"):
                UPD(newmsg[2])
            elif(receivedMSG == "DWNTrue"):
                DWN(newmsg[2])
            elif(receivedMSG == "See ya, mate"):
                print(receivedMSG)
                break
            elif(receivedMSG == "server is SHUTING DOWN"):
                SHT = True
                print(receivedMSG)
                sys.exit(0)
            else:
                print(receivedMSG)

def newThread():
    thread = threading.Thread(target=receive)
    thread.setDaemon(True)
    thread.start()

def UPD(filename):
    f = open(filename, "r")
    segment = f.read(2048)
    while(segment):
        print(f"sending...")
        clientSocket.send(segment.encode())
        segment = f.read(2048)
    clientSocket.send("done".encode())
    f.close()

def DWN(filename):
    f = open(filename, "w")
    segment = clientSocket.recv(2048).decode()
    while(segment != "done"):
        print(f"receiving...")
        f.write(segment)
        segment = clientSocket.recv(2048).decode()
    f.close()
    with open(filename, "r") as f:
        lines = f.readlines()[0:-1]
    f.close()
    with open(filename, "w") as f:
        for line in lines:
            f.write(line)
    f.close()

if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    clientStart(host, port)