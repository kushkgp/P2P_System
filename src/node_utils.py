from collections import defaultdict
from utils import *
from env import *
import time
import json
import os
import socket

def get_hublist():
	addr = (WEB_CACHE_IP,WEB_CACHE_TCP_PORT)
	s = initTCPSocket(addr)
	sendTCP(s,("req",))
	response = recvTCP(s)
	return response[0], response[1]

def connect_hub(ip, a, isLeaf):
	addr = (ip, HUB_TCP_PORT)
	s = initTCPSocket(addr)
	sendTCP(s, ("updateQHT",a.get_aggregateQHT(), isLeaf))
	a.neighbours[ip] = recvTCP(s)
	s.close()

def joinCluster(a, CLUSTER_LIMIT, isLeaf):
	try:
		selfip, a.hublist = get_hublist()
		a.hublist.pop(selfip)
		# todo sort hublist by no. of leaves/hubs
		for nbr in a.neighbours:
			if nbr not in a.hublist:
				a.neighbours.pop(nbr)
		x = len(a.neighbours)
		for hub in a.hublist:
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
