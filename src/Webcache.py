import socket
import pickle as pkl
from collections import defaultdict
from utils import *
from env import *

HUB_TCP_PORT = 21000

from env import *
class WebCache:
	def __init__(self, file = None):
		if file is not None:
			self.__hublist = pkl.load(open(file,'r'))
		else:	
			self.__hublist = defaultdict(lambda:(0,0))
	# def start(self):
	# 	host = ''
	# 	port = 50196
	# 	backlog = 5
	# 	size = 1024
		
	# 	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
	# 	s.bind((host,port))
	# 	print "socket binded to %s" %(port)
		
	# 	s.listen(backlog)
	# 	# put the socket into listening mode
	# 	print "Web cache is listening"           
		 
	# 	# a forever loop until we interrupt it or 
	# 	# an error occurs
	# 	while True:
	# 	   # Establish connection with client.
	# 	   c, addr = s.accept()     
	# 	   print 'Got connection from', addr
	# 	   # send a thank you message to the client. 
	# 	   c.send('Thank you for connecting')
	# 	   req = c.recv(3)
	# 	   print req
	# 	   c.send("FO")
	# 	   # Close the connection with the client
	# 	   c.close() 
	def add(self, sender_ip, conn_cnt=(0,0), isTemp=0):
		print "Active hub count is : ", len(self.__hublist)
		if isTemp:
			if len(self.__hublist) > MIN_HUB_COUNT:
				try:
					addr = (sender_ip,LEAF_UDP_PORT)
					sendUDPpacket(addr, ("remove_temphub", sender_ip))
					print "Request sent to Leaf ", sender_ip, " to remove HUB"
				except Exception as e:
					print e.message
		self.__hublist[sender_ip] = conn_cnt

	def remove(self, sender_ip, ip):
		if ip in self.__hublist:
			self.__hublist.pop(ip)
	
	def request(self, sender_ip, isLeaf):
		if isLeaf:
			try:
				if len(self.__hublist) < MIN_HUB_COUNT and sender_ip not in self.__hublist:
					addr = (sender_ip,LEAF_UDP_PORT)
					sendUDPpacket(addr, ("start_temphub",))
					print "Request sent to Leaf ", sender_ip, " to become HUB"
			except Exception as e:
				print e.message

		return (sender_ip, self.__hublist)

a = WebCache()
func_map = {"add":a.add, "req":a.request, "rem":a.remove}
select_call(func_map, WEB_CACHE_TCP_PORT, WEB_CACHE_UDP_PORT)

