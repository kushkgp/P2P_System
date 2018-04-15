from collections import defaultdict
from utils import *
from env import *
import time
import json
import os
import socket

def get_hublist(isLeaf):
	addr_flag = 1;
	addr1 = (WEB_CACHE_IP_1,WEB_CACHE_TCP_PORT)
	addr2 = (WEB_CACHE_IP_2,WEB_CACHE_TCP_PORT)
	while True:
		try:
			addr = addr1
			if addr_flag==2:
				addr = addr2
			print "Trying to connect to Webcache at ", addr
			s = initTCPSocket(addr)
			sendTCP(s,("req", isLeaf))
			response = recvTCP(s)
			if not isLeaf and response[0] in response[1]:
				response[1].pop(response[0])
			return response[1]
		except Exception as e:
			print "Error connecting with web Cache at ",addr,": ",e.message
		finally:
			if addr_flag == 1:
				addr_flag = 2
			else:
				addr_flag = 1

def connect_hub(ip, a, mutex, isLeaf):
	addr = (ip, HUB_TCP_PORT)
	s = initTCPSocket(addr)
	mutex.acquire()
	b = copy.deepcopy(a.get_aggregateQHT())
	mutex.release()
	sendTCP(s, ("updateQHT",b, isLeaf))
	
	b = recvTCP(s)
	mutex.acquire()
	a.neighbours[ip] = b
	mutex.release()
	s.close()

def joinCluster(a, mutex, CLUSTER_LIMIT, isLeaf):
	try:
		b = get_hublist(isLeaf)
		mutex.acquire()
		a.hublist = b
		# sorting hublist by no. of leaves/hubs
		sorted_tuples = sorted(a.hublist.items(),key=lambda x: x[1][1-isLeaf])
		mutex.release()

		mutex.acquire()
		for nbr in a.neighbours:
			if nbr not in a.hublist:
				a.neighbours.pop(nbr)
		mutex.release()
		
		for hub_tuple in sorted_tuples:
			hub = hub_tuple[0]
			mutex.acquire()
			if hub not in a.neighbours:
				mutex.release()
				try:
					connect_hub(hub, a, mutex, isLeaf)
				except Exception as e:
					print e.message
				finally:
					mutex.acquire()
					x = len(a.neighbours)
					mutex.release()
					if x >= CLUSTER_LIMIT:
						break
					continue
			else:
				mutex.release()
	except Exception as e:
		print e.message
