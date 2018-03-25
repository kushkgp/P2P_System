import socket
from collections import defaultdict
import json
from random import randint
import select, socket, sys, Queue
WC_TCP_PORT = 50000
WC_UDP_PORT = 15000
#Port : 
def initUDPrecvSocket(port):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('',port))
	return s

def sendUDPpacket(addr, msg):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.bind(('',randint(10000,60000)))
		msg = json.dumps(msg).encode()
		s.sendto(msg, addr)
	except Exception as e:
		print e.message
	s.close()

def recvUDPpacket(s):
	message, address = s.recvfrom(1024)
	return message, address

def abc():
	print "yoyo"

# func_map = {"kush":abc}

def send_data(skt, data):
	totalsent = 0
	while totalsent < len(data):
		sent = skt.send(data[totalsent:])
		if sent == 0:
			raise RuntimeError("socket connection broken")
		totalsent = totalsent + sent

def select_call(func_map):
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setblocking(0)
	server.bind(('', WC_TCP_PORT))
	server.listen(5)
	TCPserver = server
	
	skt = initUDPrecvSocket(WC_UDP_PORT)

	UPDservers = [skt]
	TCPservers = []

	inputs = [server,skt]
	outputs = []

	message_queues = {}
	client_addresses = defaultdict()
	while inputs:
		print "---=-=-=-=--=-=-=-=-=--==--=-=-=-=--=--=-=-=-=---=--=-=-=-=-"
		print len(inputs)
		readable, writable, exceptional = select.select(inputs, outputs, inputs)
		for s in readable:
			if s is TCPserver:
				print "New incoming TCP connection"
				connection, client_address = s.accept()
				client_addresses[connection] = client_address
				connection.setblocking(0)
				inputs.append(connection)
				TCPservers.append(connection)
			elif s in TCPservers:
				msg = s.recv(1024)
				print msg
				if msg == "" or msg is None:
					print "Client closed TCP connection ",client_addresses[s]
					client_addresses.pop(s)
					inputs.remove(s)
					TCPservers.remove(s)
					continue

				addr = client_addresses[s]
				print "TCP packet received from ", client_addresses[s]
				print msg
				inp = json.loads(msg)
				print inp
				try:
					print "func : ", inp[0], "called by ", addr[0], " with args : ", inp[1:]
					data = func_map[inp[0]](addr[0],*inp[1:])
					print data
					ret_data = json.dumps(data)
					send_data(s,ret_data)
				except Exception as e:
					print e.message

			elif s in UPDservers:
				msg, addr = s.recvfrom(1024)
				print "UDP packet received from ", addr
				inp = json.loads(msg)
				print inp
				try:
					print "func : ", inp[0], "called by ", addr[0], " with args : ", inp[1:]
					func_map[inp[0]](addr[0],*inp[1:])
				except Exception as e:
					print e.message
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
			print "something"
			try:
				next_msg = message_queues[s].get_nowait()
			except Queue.Empty:
				outputs.remove(s)
			else:
				s.send(next_msg)

		for s in exceptional:
			print "Left"
			inputs.remove(s)
			if s in outputs:
				outputs.remove(s)
			s.close()
			del message_queues[s]


# select_call()