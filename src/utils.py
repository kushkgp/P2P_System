import socket
from collections import defaultdict
import pickle as pkl
from random import randint
import select, socket, sys, Queue
<<<<<<< HEAD

HUB_TCP_PORT = 21000

=======
>>>>>>> 522d35f8d8386d75bdebdd1f1ad64d4c509d4b29
#Port : 
def initUDPrecvSocket(port):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('',port))
	return s

def sendUDPpacket(addr, msg):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.bind('',randint(10000,60000))
<<<<<<< HEAD
		msg = pkl.dumps(msg).encode()
		s.sendto(msg, addr)
	except Exception as e:
		print e.message
=======
		s.sendto(msg, addr)
	except Exception(e):
		print e
>>>>>>> 522d35f8d8386d75bdebdd1f1ad64d4c509d4b29
	s.close()

def recvUDPpacket(s):
	message, address = s.recvfrom(1024)
	return message, address

def abc():
	print "yoyo"

<<<<<<< HEAD
# func_map = {"kush":abc}

def select_call(func_map):
=======
func_map = {"kush":abc}

def select_call():
>>>>>>> 522d35f8d8386d75bdebdd1f1ad64d4c509d4b29

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	server.setblocking(0)
	server.bind(('', 50000))
	server.listen(5)
	
	skt = initUDPrecvSocket(15000)
	
	UPDservers = [skt]
	TCPservers = [server]

	inputs = [server,skt]
	outputs = []
	message_queues = {}

	while inputs:
		print len(inputs)
		readable, writable, exceptional = select.select(inputs, outputs, inputs)
		for s in readable:
			if s in TCPservers:
				print "New incoming TCP connection"
				connection, client_address = s.accept()
				connection.setblocking(0)
				inputs.append(connection)
				message_queues[connection] = Queue.Queue()
			elif s in UPDservers:
<<<<<<< HEAD
				msg, addr = s.recvfrom(1024)
				print "UDP packet received from ", addr
				inp = pkl.loads(msg)
				print inp
				try:
					func_map[inp[0]](addr[0],*inp[1:])
				except Exception as e:
					print e.message
=======
				print "UDP packet received"
				msg, addr = s.recvfrom(1024)
				print msg
				func_map[msg]()
>>>>>>> 522d35f8d8386d75bdebdd1f1ad64d4c509d4b29
			else:
				print "gulab"
				data = s.recv(1024)
				print data is None
				if data:
					message_queues[s].put(data)
					if s not in outputs:
						outputs.append(s)
				else:
					if s in outputs:
						outputs.remove(s)
					inputs.remove(s)
					s.close()
					del message_queues[s]

		for s in writable:
<<<<<<< HEAD
			print "something in writable"
=======
			print "something"
>>>>>>> 522d35f8d8386d75bdebdd1f1ad64d4c509d4b29
			try:
				next_msg = message_queues[s].get_nowait()
			except Queue.Empty:
				outputs.remove(s)
<<<<<<< HEAD
				print "No message sent"
			else:
				s.send(next_msg)
				print "Message sent"
=======
			else:
				s.send(next_msg)
>>>>>>> 522d35f8d8386d75bdebdd1f1ad64d4c509d4b29

		for s in exceptional:
			print "Left"
			inputs.remove(s)
			if s in outputs:
				outputs.remove(s)
			s.close()
			del message_queues[s]

<<<<<<< HEAD
=======

select_call()
>>>>>>> 522d35f8d8386d75bdebdd1f1ad64d4c509d4b29
