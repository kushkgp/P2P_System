import socket
import pickle as pkl
from collections import defaultdict
from utils import *
HUB_TCP_PORT = 21000
class WebCache:
	__hublist = []
	def __init__(self, file = None):
		if file is not None:
			self.__hublist = pkl.load(open(file,'r'))
		else:	
			self.__hublist = [2]
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
	def add(self,ip, port=HUB_TCP_PORT, conn_cnt=(0,0)):
		self.__hublist[(ip,port)] = conn_cnt

	def remove(self,ip, port=HUB_TCP_PORT):
		if (ip,port) in __hublist:
			self.__hublist.pop((ip,port))
	
	def request(self):
		return self.__hublist

a = WebCache()
func_map = {"add":a.add}

select_call(func_map)

