from socket import *
import os
import sys
import pickle
import time
import glob
import threading

userInfo = {}
threads = []
users = []
adminPassword = "admin"
SHT = False
clientSockets = {}


def serverStart(connectionSocket):
    global clientSockets
    global SHT
    global users
    connected = False
    currentUser = ""
    global threads
    while(1):
        connected = True
        print(f"Client connected")
        auth = False
        while(1):
            try:
                receivedMSG = connectionSocket.recv(2048)
            except ConnectionResetError:
                sys.exit(0)
            if(not auth):
                packet = []
                username = receivedMSG.decode()
                if(username not in userInfo):
                    msg = "The user doesn't exist!"
                    packet.append(msg)
                    packet.append(False)
                    connectionSocket.send(pickle.dumps(packet))
                    print(msg + "\nNow registing")
                    password = connectionSocket.recv(2048).decode()
                    userInfo[username] = password
                    packet = []
                    msg = "Welcome to the forum!"
                    currentUser = username
                    packet.append(msg)
                    packet.append(True)
                    connectionSocket.send(pickle.dumps(packet))
                    f = open("credentials.txt", "a")
                    f.write(username + " " + password + "\n")
                    f.close()
                    clientSockets[username] = connectionSocket
                    users.append(username)
                    auth = True
                elif(username in userInfo):
                    if(username in users):
                        print(f"The user already logged in")
                        packet.append("The user already logged in")
                        packet.append(False)
                        connectionSocket.send(pickle.dumps(packet))
                    else:
                        print(f"The user name matched")
                        packet.append("")
                        packet.append(True)
                        connectionSocket.send(pickle.dumps(packet))
                        password = connectionSocket.recv(2048).decode()
                        packet = []
                        if(str(password) == str(userInfo[username])):
                            print(f"Authenticated")
                            msg = "Welcome to the forum!"
                            packet.append(msg)
                            packet.append(True)
                            connectionSocket.send(pickle.dumps(packet))
                            currentUser = username
                            clientSockets[username] = connectionSocket
                            users.append(username)
                            auth = True
                        else:
                            print(f"Wrong password!")
                            msg = "Invalid password, please try again!"
                            packet.append(msg)
                            packet.append(False)
                            connectionSocket.send(pickle.dumps(packet))
            else:
                if(not connected):
                    break
                command = receivedMSG.decode().split()
                if(len(command) == 0):
                    continue
                if(not checkCommand(command)):
                    connectionSocket.send("Invalid command".encode())
                else:
                    if(os.path.exists("ThreadList") and len(threads) == 0):
                        with open("ThreadList", "r") as f:
                            lines = f.readlines()
                        f.close()
                        for line in lines:
                            threads.append(line.rstrip())
                    print(threads)
                    msg = executeCommand(command, connectionSocket, currentUser)
                    connectionSocket.send(msg.encode())
                    if(msg == "See ya, mate"):
                        connected = False
        if(not connected):
            break
        if(SHT):
            break
    if(threading.active_count() == 2):
            print(f"Waiting for clients")
            

def checkCommand(command):
    vaildCommand = ["CRT", "MSG", "DLT", "EDT", "LST", "RDT", "UPD", "DWN", "RMV", "XIT", "SHT"]
    if(command[0] in vaildCommand):
        return True
    return False

def executeCommand(command, connectionSocket, currentUser):
    global threads
    global clientSockets
    global SHT
    global users
    msg = ""
    if(command[0] == "CRT"):
        if(len(command) != 2):
            msg = "Incorrect syntax for CRT"
        elif(command[1] in threads):
            msg = "Thread " + command[1] + " exists"
        elif(command[1] == "ThreadList"):
            msg = "Can't use this name, try others!"
        else:
            print(currentUser + " issued LST command")
            threads.append(command[1])
            msg = "Thread " + command[1] + " created"
            newThread = open(command[1], "w")
            newThread.write(currentUser + "\n")
            newThread.close()
            newThread = open("ThreadList", "a")
            newThread.write(command[1] + "\n")
            newThread.close()
            print(msg)
    elif(command[0] == "MSG"):
        if(len(command) <= 2):
            msg = "Incorrect syntax for MSG"
        elif(command[1] not in threads):
            msg = "Thread " + command[1] + " is not exist"
        else:
            print(currentUser + " issued LST command")
            count = countLine(command[1])
            msg = "Message posted to " + command[1] + " thread"
            newThread = open(command[1], "a")
            command = command[2:]
            command = " ".join(command)
            newThread.write(str(count) + " " + currentUser + ": " + command + "\n")
            newThread.close()
            print(msg)
    elif(command[0] == "DLT"):
        if(len(command) != 3):
            msg = "Incorrect syntax for DLT"
        elif(command[1] not in threads):
            msg = "Thread " + command[1] + " is not exist"
        elif(int(command[2]) > countLine(command[1])):
            msg = "The message number " + command[2] + " doesn't exist"
        else:
            print(currentUser + " issued DLT command")
            flag = False
            with open(command[1], "r") as f:
                lines = f.readlines()
            f.close()
            with open(command[1], "w") as f:   
                for line in lines:
                    newline = line.split()
                    if(len(newline) == 1):
                        f.write(line)
                    elif(command[2] != newline[0] or currentUser + ":" != newline[1]):
                        f.write(line)
                    elif(command[2] == newline[0] and currentUser+ ":" == newline[1]):
                        flag = True

            f.close()
            if(flag):
                updateMSGNumber(command[1])
                msg = currentUser + " deleted the message number " + command[2] + " from thread " + command[1]
            else:
                msg = "You are not the user originally posted that message"
    elif(command[0] == "EDT"):
        if(len(command) != 4):
            msg = "Incorrect syntax for EDT"
        elif(command[1] not in threads):
            msg = "Thread " + command[1] + " is not exist"
        elif(int(command[2]) > countLine(command[1])):
            msg = "The message number " + command[2] + " doesn't exist"
        else:
            print(currentUser + " issued EDT command")
            flag = False
            with open(command[1], "r") as f:
                lines = f.readlines()
            f.close()
            
            newlines = []

            for line in lines:
                newline = line.split()
                if(len(newline) != 1):
                    if(command[2] == newline[0] and currentUser + ":" == newline[1]):
                        newstr = newline[0] + " " + newline[1] + " " + command[3]
                        line = line.replace(line, newstr)
                        newlines.append(line)
                        msg = currentUser + " changed the message with number " + command[2] + " into " + command[3] + " from thread " + command[1]
                        flag = True
                    elif(command[2] == newline[0]):
                        msg = "You are not the user originally posted that message"
                        break
                    else:
                        newlines.append(line)
                else:
                    newlines.append(line)

            if(flag):
                f = open(command[1], "w")
                for line in newlines:
                    f.write(line)
                f.close()
    elif(command[0] == "LST"):
        if(len(command) != 1):
            msg = "Incorrect syntax for LST"
        elif(len(threads) != 0):
            msg = "The list of active threads:\n"
            for tread in threads:
                msg += tread
                msg += "\n"
        else:
            msg = "No threads to list"
        print(currentUser + " issued LST command")
    elif(command[0] == "RDT"):
        if(len(command) != 2):
            msg = "Incorrect syntax for RDT"
        elif(command[1] in threads):
            with open(command[1], "r") as f:
                lines = f.readlines()[1:]
            f.close()
            if(len(lines) == 0):
                msg = "Thread " + command[1] + " is empty"
            else:
                for line in lines:
                    msg += line
    elif(command[0] == "UPD"):
        if(len(command) != 3):
            msg = "Incorrect syntax for UPD"
        elif(command[1] in threads):
            connectionSocket.send("UPDTrue".encode())
            print(currentUser + " issued UPD command")
            filename = command[1] + "-" + command[2]
            f = open(filename, "w")
            segment = connectionSocket.recv(2048).decode()
            while(segment != "done"):
                print(f"receiving...")
                f.write(segment)
                segment = connectionSocket.recv(2048).decode()
            f.write("\n" + currentUser + " uploaded " + command[2] + "\n")
            f.close()
            print(currentUser + " uploaded file " + command[2] + " to " + command[1] + " thread")
            msg = command[2] + " uploaded to " + command[1] + " thread"
        else:
            msg = "Thread " + command[1] + " is not exist"
    elif(command[0] == "DWN"):
        if(len(command) != 3):
            msg = "Incorrect syntax for DWN"
        elif(command[1] in threads):
            filename = command[1] + "-" + command[2]
            if(os.path.exists(filename)):
                connectionSocket.send("DWNTrue".encode())
                print(currentUser + " issued DWN command")
                f = open(filename, "r")
                segment = f.read(2048)
                while(segment):
                    print(f"sending...")
                    connectionSocket.send(segment.encode())
                    segment = f.read(2048)
                time.sleep(0.1)
                connectionSocket.send("done".encode())
                f.close()
                print(command[2] + " downloaded from Tread " + command[1])
                msg = command[2] + " successfully downloaded"
            else:
                print(command[2] + " does not exist in Thread " + command[1])
                msg = command[2] + " does not exist in Thread " + command[1]
        else:
            msg = "Thread " + command[1] + " is not exist"
    elif(command[0] == "RMV"):
        if(len(command) != 2):
            msg = "Incorrect syntax for RMV"
        elif(command[1] in threads):
            f = open(command[1], "r")
            line = f.readline()
            f.close()
            if(line.rstrip() == currentUser):
                fname = command[1] + "*"
                for filename in glob.glob(fname):
                    os.remove(filename)
                with open("ThreadList", "r") as f:
                    lines = f.readlines()
                f.close()
                with open("ThreadList", "w") as f:   
                    for line in lines:
                        if(line != command[1]):
                            f.write(line)
            else:
                msg = "The thread was created by another user and cannot be removed"
                print("Thread " + command[1] + " cannot be removed")
        else:
            msg = "Thread " + command[1] + " is not exist"
    elif(command[0] == "XIT"):
        if(len(command) != 1):
            msg = "Incorrect syntax for XIT"
        else:
            del clientSockets[currentUser]
            users.remove(currentUser)
            msg = "See ya, mate"
    elif(command[0] == "SHT"):
        if(len(command) != 2):
            msg = "Incorrect syntax for SHT"
        elif(command[1] == adminPassword):
            SHT = True
            msg = "server is SHUTING DOWN"
            for client in clientSockets.values():
                if(client == connectionSocket):
                    continue
                client.send(msg.encode())
            users = []
            threads = []
            clientSockets = {}
            f = open("ThreadList", "r")
            for line in f.readlines():
                fname = line.rstrip() + "*"
                for filename in glob.glob(fname):
                    os.remove(filename)
            f.close()
            os.remove("ThreadList")
            os.remove("credentials.txt")
        else:
            msg = "Wrong password"



    return msg

def updateMSGNumber(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    f.close()
    with open(filename, "w") as f:
        count = 1
        for line in lines:
            newline = line.split()
            if(len(newline) == 1):
                f.write(line)
            else:
                newline[0] = str(count)
                newline = " ".join(newline)
                count = count + 1
                f.write(newline + "\n")
    f.close()

def newThread(port):
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('localhost', port))
    serverSocket.listen(1)
    print(f"Waiting for clients")
    while(1):
        connectionSocket, addr = serverSocket.accept()
        if(SHT):
            break
        thread = threading.Thread(target=serverStart, args=(connectionSocket,))
        thread.setDaemon(True)
        thread.start()


def countLine(filename):
    count = 0
    f = open(filename,"r")
    for line in f.readlines():
        count = count + 1
    f.close()
    return count

def readUserInfo():
    global userInfo
    if(os.path.exists("credentials.txt")):
        credentialFile = open("credentials.txt")
        line = credentialFile.readline()
        while(line):
            user = line.split()
            username = user[0]
            password = user[1]
            userInfo[username] = password
            line = credentialFile.readline()
        print("User info as following:")
        print(userInfo)
        print("\n")

if __name__ == "__main__":
    port = int(sys.argv[1])
    readUserInfo()
    mainThread = threading.current_thread()
    newThread(port)

