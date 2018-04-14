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
			s = initTCPSocket(addr)
			sendTCP(s,("req",))
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

def connect_hub(ip, a, isLeaf):
	addr = (ip, HUB_TCP_PORT)
	s = initTCPSocket(addr)
	sendTCP(s, ("updateQHT",a.get_aggregateQHT(), isLeaf))
	a.neighbours[ip] = recvTCP(s)
	s.close()

def joinCluster(a, CLUSTER_LIMIT, isLeaf):
	try:
		a.hublist = get_hublist(isLeaf)
		sorted_tuples = sorted(a.hublist.items(),key=lambda x: x[1][1-isLeaf])
		# todo sort hublist by no. of leaves/hubs
		for nbr in a.neighbours:
			if nbr not in a.hublist:
				a.neighbours.pop(nbr)
		x = len(a.neighbours)
		
		for hub_tuple in sorted_tuples:
			hub = hub_tuple[0]
			if hub not in a.neighbours:
				try:
					connect_hub(hub, a, isLeaf)
					x+=1
					if x >= CLUSTER_LIMIT:
						break
				except Exception as e:
					print e.message
					continue
	except Exception as e:
		print e.message
