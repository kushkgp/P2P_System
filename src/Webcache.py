import socket
from collections import defaultdict
import pickle as pkl

class WebCache:
	def __init__(self, file = None):
		if file is not None:
			self.__hublist = pkl.load(open(file,'r'))
		else:	
			self.__hublist = defaultdict(lambda:0)
	def start(self):
		host = ''
		port = 50196
		backlog = 5
		size = 1024
		
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		s.bind((host,port))
		print "socket binded to %s" %(port)
		
		s.listen(backlog)
		# put the socket into listening mode
		print "Web cache is listening"           
		 
		# a forever loop until we interrupt it or 
		# an error occurs
		while True:
		   # Establish connection with client.
		   c, addr = s.accept()     
		   print 'Got connection from', addr
		   # send a thank you message to the client. 
		   c.send('Thank you for connecting')
		   req = c.recv(3)
		   print req
		   c.send("FO")
		   # Close the connection with the client
		   c.close()

	def add(ip, port, leaf_cnt=0):
		__hublist[(ip,port)] = leaf_cnt

	def remove(ip, port):
		if (ip,port) in __hublist:
			__hublist.pop((ip,port))
	
	def request():
		return __hublist

a = WebCache()
a.start()
# print a.__hublist

