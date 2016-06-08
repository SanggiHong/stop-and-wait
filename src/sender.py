import os
import socket
import sys
import time
import random
import time

FILE_BUFFER_SIZE = 1471
SEND_BUFFER_SIZE = 1472

if(len(sys.argv) < 3):
	print "[Dest IP Addr] [Dest Port] [File Path]"
	sys.exit()

serverIP = sys.argv[1]
serverPort = int(sys.argv[2])
filePath = sys.argv[3]

try:
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	########################################################
	#              CONNECTION SEQUENCE START               #
	########################################################

	myKey = random.randrange(0,2);
	sock.settimeout(50)
	sock.sendto(str(myKey), (serverIP, serverPort))
	
	#Receive respond key
	#Key is "1" if myKey is 0
	# or is "0" if myKey is 1
	try:
		key, addr = sock.recvfrom(1)
	except socket.timeout as e:
		print "Receiver didn't respond"
		sys.exit()

	#Key check
	if ( (int(key) ^ myKey) == 1):
		print "Server Connected..."
		print "Server address :", addr[0]
	else:
		print "Connection key Error"
		sys.exit()

	########################################################
	#                CONNECTION SEQUENCE END               #
	########################################################
	
	########################################################
	#                 FILE TRANSFER START                  #
	########################################################
	with open(filePath, 'rb') as f:
		fileSize = os.stat(filePath).st_size	
		sock.sendto(filePath, (serverIP, serverPort))
		sock.sendto(str(fileSize), (serverIP, serverPort))

		transferred = 0
		receivedSequenceNumber = 1
		sequenceNumber = 1
		sock.settimeout(2)
		start_time = time.time()
		while(transferred < fileSize):
			if(receivedSequenceNumber == sequenceNumber):
				sequenceNumber ^= 1
				fileBuffer = str(sequenceNumber) + f.read(FILE_BUFFER_SIZE)
			sock.sendto(fileBuffer, (serverIP, serverPort))
			########################################################
			#              	 STOP AND WAIT SEQUENCE                #
			########################################################
			try:
				receivedSequenceNumber, addr = sock.recvfrom(1)
				receivedSequenceNumber = int(receivedSequenceNumber)
				if(receivedSequenceNumber == sequenceNumber):
					transferred += FILE_BUFFER_SIZE
					if(transferred > fileSize):
						transferred = fileSize
					print transferred, "/", fileSize, \
					"(Current size / Total size),", \
					round(float(transferred)/fileSize*100, 2), "%"
				else:
					print "Wrong number ACK was discarded"
			except socket.timeout as e:
				print e
			########################################################
			#                  STOP AND WAIT END                   #
			########################################################
		end_time = time.time()
		print "Completed..."
		print "Time elapsed :", str( end_time - start_time )
	########################################################
	#                  FILE TRANSFER END                   #	
	########################################################
except socket.error as e:
	print e
	sys.exit()
