import socket
import sys
import time

UDP_IP = ""
UDP_PORT = 5005
RECEIVE_BUFFER_SIZE = 1472
FILE_BUFFER_SIZE = 1471

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print "ready for client..."
try:
	#Connection test, correct connection key is "0" or "1"
	key, addr = sock.recvfrom(1)
	if(key in ["0", "1"]):
		response = int(key)^1
		sock.sendto(str(response), addr)
		print "Client address :", addr[0]
	else:
		print "Unexpected Client Error"
		sys.exit()

	filePath, addr = sock.recvfrom(RECEIVE_BUFFER_SIZE)
	print "FileName :", filePath
	fileSize, addr = sock.recvfrom(RECEIVE_BUFFER_SIZE)
	print "FileSize :", fileSize
	fileSize = int(fileSize)
	with open(filePath, "wb") as f:
		received = 0
		sequenceNumber = 0
		receivedSequenceNumber = -1
		start_time = time.time()
		while (received < fileSize):
			fileBuffer, addr = sock.recvfrom(RECEIVE_BUFFER_SIZE)
			receivedSequenceNumber = int(fileBuffer[0])
			if(receivedSequenceNumber != sequenceNumber):
				print "Wrong Sequence frame was discarded"
				sock.sendto(str(receivedSequenceNumber), addr)
				continue
			sock.sendto(str(receivedSequenceNumber), addr)	
			fileBuffer = fileBuffer[1:]
			f.write(fileBuffer)
			received += FILE_BUFFER_SIZE
			if(received > fileSize):
				received = fileSize
			print received, "/", fileSize, \
			"(Current size / Total size),", \
			round(float(received)/fileSize*100, 2), "%"
			sequenceNumber ^= 1
		end_time = time.time()
		print "Completed..."
		print "Time elapsed :", str( end_time - start_time )
except socket.error as e:
	print e
	sys.exit()

