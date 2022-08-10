from receiver import pack_flags, unpack_flags, make_TCP_PACK, make_TCP_UNPACK
from sys import argv
import socket
import receiver
import argparse
import random
import struct
import ast
import textwrap

def createListOfPackets(readB):
    n=488
    parts = [readB[i:i+n] for i in range(0, len(readB), n)]
    
    return parts

def makeHeader(args,sequenceNumber,ackNumber):
    header=make_TCP_PACK(source_port=args.myport,dest_port=args.theirport,sequence_number=sequenceNumber,ack_number=ackNumber)
    
    return header

def main():
    inputFile = "test-input.txt"

    parser = argparse.ArgumentParser()
    parser.add_argument('myport', type=int)
    parser.add_argument('receiver_address', type=str)
    parser.add_argument('theirport', type=int)
    parser.add_argument('window', nargs='?', type=int, default=-1)
    args = parser.parse_args(argv[1:])

    ssocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ssocket.bind(('', args.myport))
    ssocket.connect((args.receiver_address, args.theirport))

    ssocket.settimeout(0.1)

    
    # stop and wait
    
    recv=''
    prevrecv=recv
    
    sequenceNumber=0
    ackNumber=0
    
    totalSent=0
    
    with open(inputFile,"rb") as f:
        readByte=f.read(488)
        while readByte!=b"":
            header=make_TCP_PACK(source_port=args.myport,dest_port=args.theirport,sequence_number=sequenceNumber,ack_number=ackNumber)
            ssocket.send(header+readByte)
            
            
            while recv==prevrecv:
                try:
                    recv=make_TCP_UNPACK(ssocket.recv(512))
                except:
                    ssocket.send(header+readByte)
            
            if(len(readByte)==488):
                while recv['ack_number']%488!=0:
                    try:
                        recv=make_TCP_UNPACK(ssocket.recv(512))
                    except:
                        ssocket.send(header+readByte)
            else:
                while recv['ack_number']!=totalSent+len(readByte):
                    try:
                        recv=make_TCP_UNPACK(ssocket.recv(512))
                    except:
                        ssocket.send(header+readByte)
            
            
            # print(recv)
            prevrecv=recv
            
            print(recv)
            sequenceNumber=recv['ack_number']
            ackNumber=recv['ack_number']
            
            totalSent+=488
            readByte=f.read(488)
        
        header=make_TCP_PACK(sequence_number=sequenceNumber,ack_number=ackNumber,FIN=1)
        ssocket.send(header+b'fuck off')

    ssocket.close()



if __name__ == '__main__':
    main()