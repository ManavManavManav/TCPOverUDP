from struct import pack
from receiver import pack_flags, unpack_flags, make_TCP_PACK, make_TCP_UNPACK
from sys import argv
import socket
import argparse
from select import select
import os

def packetAssocList(list):
    ret=[]
    tally=len(list[0])
    for i in list:
        ret.append([tally,i])
        tally+=len(list[0])
    return ret
    
def makeHeader(args,sequenceNumber,ackNumber):
    header=make_TCP_PACK(source_port=args.myport,dest_port=args.theirport,sequence_number=sequenceNumber,ack_number=ackNumber)
    
    return header
    
def createListOfPackets(readB,n):
    n=n if n<488 else 488
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
    parser.add_argument('window', nargs='?', type=int, default=488)
    args = parser.parse_args(argv[1:])

    ssocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ssocket.bind(('', args.myport))
    ssocket.connect((args.receiver_address, args.theirport))
        
    window = args.window
    sequenceNumber=0
    ackNumber=0

    packetSize=488 if window>488 else window
    dick=[]
    readB=''
    with open(inputFile, "rb") as f:
        readB = f.read()
        dick=packetAssocList(createListOfPackets(readB,window))
    
    maxPacketsAtATime=int(window/488) if window>488 else 1
    curLastPacketId=maxPacketsAtATime
    packetSize=window if window<488 else 488
           
    
    
    goodAcks=[]
    print(len(readB)/packetSize)
    for i in range(int(len(readB)/packetSize)):
        goodAcks.append(i*packetSize)
    goodAcks.append(len(readB))
    
    
    for i in range(len(readB)-packetSize,len(readB)):
        goodAcks.append(i)
    
    
    
    
    indexIntial=0
    # print(goodAcks)
    while True:
        for i in range(indexIntial,indexIntial+maxPacketsAtATime): 
            # print(indexIntial)
            try:
                sequenceNumber=dick[i][0]-packetSize
                print(sequenceNumber)
            except:
                break
            header=makeHeader(args,sequenceNumber,dick[i][0])
            packet=header+dick[i][1]
            ssocket.send(packet)
            
            readable,_,_=select([ssocket],[],[],0.1)
            if(readable):
                recv=make_TCP_UNPACK(readable[0].recv(512))
                if recv['ack_number'] in goodAcks:
                    ackNumber=max(recv['ack_number'],ackNumber)
                    indexIntial=int(ackNumber/packetSize)
            
        if(ackNumber==len(readB)):
            break
    
    # firstPacketNumber=0
    # print(len(readB))
    # while True:
    #     for i in range(firstPacketNumber,curLastPacketId):
    #         header=makeHeader(args,sequenceNumber,dick[i][0])
    #         packet=header+dick[i][1]
    #         ssocket.send(packet)
    #         readable,_,_=select([ssocket],[],[],0)
    #         if(readable):
    #             recv=make_TCP_UNPACK(ssocket.recv(512))
    #             ackNumber=max(recv['ack_number'],ackNumber)
    #             print(ackNumber)
    #             packetsConsumed=(ackNumber/packetSize)-firstPacketNumber
    #             firstPacketNumber+=packetsConsumed
    #             curLastPacketId+=packetsConsumed
    #             print(firstPacketNumber)
    #             print(curLastPacketId)
                
    #     if(ackNumber==len(readB)):
    #         break
          
            
    #closing socket
    header=make_TCP_PACK(sequence_number=sequenceNumber,ack_number=ackNumber,FIN=1)
    ssocket.send(header+b'fuck off') 
    ssocket.close()



if __name__ == '__main__':
    main()