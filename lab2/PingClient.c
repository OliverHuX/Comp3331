#include <stdio.h>
#include <stdlib.h>
#include <unistd.h> 
#include <string.h> 
#include <sys/types.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <netinet/in.h>
#define WAIT 600
#define MAX 1024

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("PingClient only accept 2 arguments Host and Port");
        return 0;
    }
    struct sockaddr_in servaddr; 
    int sockfd = socket(AF_INET, SOCK_DGRSM, 0);
    if (socket == -1) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }
    memset(&servaddr, 0, sizeof(servaddr)); 
    char *host = argv[0];
    int port = argv[1];
    servAddr.sin_familt = AF_INET;
    servAddr.sin_port = htons(port);
    servAddr.sin_addr.s_addr = inet_addr(&host);

    if(connect(sockfd, (struct sockAddr *)&servAddr, sizeof(servAddr)) == -1) { 
        perror("\n Error : Connect Failed \n"); 
        exit(EXIT_FAILURE); 
    }
    char messages = ""
    sendto(sockfd, )




}