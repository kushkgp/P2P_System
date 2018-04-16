import socket
from collections import defaultdict
import json
from random import randint
import select, socket, sys, Queue
WC_TCP_PORT = 50000
WC_UDP_PORT = 15000

# call tcp functions if you expect to get reply from the destination
def initTCPSocket(addr):
	s = socket.socket()
	s.bind(('',randint(10000,20000)))
	s.connect(addr)
	return s

def sendTCP(skt, msg):
	# print msg, "to be sent by TCP"
	data = json.dumps(msg).encode()
	totalsent = 0
	while totalsent < len(data):
		sent = skt.send(data[totalsent:])
		if sent == 0:
			raise RuntimeError("socket connection broken")
		totalsent = totalsent + sent
		# print totalsent, " bytes sent"

def recvTCP(sock):
	chunks = []
	bytes_recd = 0
	while bytes_recd%1024==0:
		chunk = sock.recv(1024)
		if chunk == b'':
			raise RuntimeError("socket connection broken")
		chunks.append(chunk)
		bytes_recd = bytes_recd + len(chunk)
		# print bytes_recd, "bytes received"
	return json.loads(b''.join(chunks))

# call udp functions
def initUDPrecvSocket(port):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('',port))
	return s

def sendUDPpacket(addr, msg):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('',randint(10000,60000)))
	msg = json.dumps(msg).encode()
	s.sendto(msg, addr)
	s.close()
# todo : test
def recvUDPpacket(s, timeout = None):
	s.settimeout(timeout)
	try:
		message, address = s.recvfrom(1024)
		return json.loads(message), address
	except socket.timeout as e:
		print e.message
		return "", None

# func_map = {"kush":abc}

def select_call(func_map, TCPport, UDPport):
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setblocking(0)
	server.bind(('', TCPport))
	server.listen(5)
	TCPserver = server
	
	skt = initUDPrecvSocket(UDPport)

	UPDservers = [skt]
	TCPservers = []

	inputs = [server,skt]
	outputs = []

	message_queues = {}
	client_addresses = defaultdict()
	while inputs:
		print "---=-=-=-=--=-=-=-=-=--==--=-=-=-=--=--=-=-=-=---=--=-=-=-=-"
		print len(inputs)
		print "---=-=-=-=--=-=-=-=-=--==--=-=-=-=--=--=-=-=-=---=--=-=-=-=-"
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
				# print msg
				if msg == "" or msg is None:
					print "Client closed TCP connection ",client_addresses[s]
					client_addresses.pop(s)
					inputs.remove(s)
					TCPservers.remove(s)
					continue

				addr = client_addresses[s]
				print "TCP packet received from ", client_addresses[s]
				# print msg
				inp = json.loads(msg)
				# print inp
				try:
					print "func : ", inp[0], "called by ", addr[0], " with args : ", inp[1:]
					data = func_map[inp[0]](addr[0],*inp[1:])
					sendTCP(s,data)
				except Exception as e:
					print e.message

			elif s in UPDservers:
				msg, addr = s.recvfrom(1024)
				print "UDP packet received from ", addr
				inp = json.loads(msg)
				# print inp
				try:
					print "func : ", inp[0], "called by ", addr[0], " with args : ", inp[1:]
					func_map[inp[0]](addr[0],*inp[1:])
				except Exception as e:
					print e.message
			else:
				# print "gulab"
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