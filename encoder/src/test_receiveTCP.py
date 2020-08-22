#!/usr/bin/env python

from socket import *
from time import ctime

HOST = '202.13.215.85'
PORT = 50007
BUFSIZE = 1024
ADDR = (HOST, PORT)

tcpSerSock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
tcpSerSock.bind(("",PORT))
tcpSerSock.listen(0)

while True:
    print('waiting for message...')
    sock, addr = tcpSerSock.accept()
    with sock:
      data = sock.recv(BUFSIZE)
      #if len(data)>0 : print('...received from {} : {}'.format(addr, data))
      print('...received from {} : {}'.format(addr, data))
      pass;
    pass;

tcpSerSock().close()
