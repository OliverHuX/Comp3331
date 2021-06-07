import sys
from socket import *

def startServer(port):
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('localhost', port))
    serverSocket.listen(1)
    print(f"The server is good to go")
    while 1:
        connectionSocket, addr = serverSocket.accept()
        packet = connectionSocket.recv(1024)
        print(f"ready to receive\n")

        try:
            info = packet.split()
            filename = info[1][1:]
            data = open(filename, "rb").read()
            print(f"file is {filename}\n")
            connectionSocket.send(b'HTTP/1.1 200 OK\r\n')
            if "png" in str(filename):
                connectionSocket.send(b'Content-Type: image/png \r\n\r\n')
            else:
                connectionSocket.send(b'Content-Type: text/html \r\n\r\n')
            connectionSocket.send(data)
        except IOError:
            connectionSocket.send(b'HTTP/1.1 404 Not Found\r\n')
            connectionSocket.send(b'Content-Type: text/html \r\n\r\n')
            connectionSocket.send(b'<html><h1>404 U r totally lost</h1></html>')

        connectionSocket.close()






if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"one argument port")
        exit(1)
    port = int(sys.argv[1])
    startServer(port)