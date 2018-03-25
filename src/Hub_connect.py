from collections import defaultdict
from Hub import Hub
from utils import *
from env import *
import threading
import time
import json

a = Hub()

def myreceive(sock):
	chunks = ""
	bytes_recd = 0
	while bytes_recd%1024==0:
		chunk = sock.recv(1024)
		if chunk == b'':
			raise RuntimeError("socket connection broken")
		chunks.append(chunk)
		bytes_recd = bytes_recd + len(chunk)
	return b''.join(chunks)

def get_hublist():
	addr = ("192.168.0.6",50000)
	s = initTCPSocket(addr)
	sendTCP(s,("req",))
	hublist = recvTCP(s)
	return hublist

def heartbeat():
	addr = (WEB_CACHE_IP,WEB_CACHE_UDP_PORT)
	while True:
		print "sending heartbeat"
		time.sleep(1)
		sendUDPpacket(addr, ("add",(a.get_leafCount(), a.get_neighbourCount()) ))

def connect_hub(ip, aggregateQHT):
	addr = (ip, HUB_TCP_PORT)
	s = initTCPSocket(addr)
	sendTCP(s, ("addhub",aggregateQHT))
	a.neighbours[ip] = recvTCP(s)

def joinCluster():
	try:
		a.hublist = get_hublist()
		# todo sort hublist by no. of hubs
		x = len(a.neighbours)
		for hub in a.hublist:
			try:
				connect_hub(hub, a.get_aggregateQHT())
				x+=1
				if x >= HUB_CLUSTER_LIMIT:
					break
			except Exception as e:
				continue
	except Exception as e:
		print e.message

def requestQHT(ip):
	addr = (ip,LEAF_TCP_PORT)
	s = initTCPSocket(addr)
	sendTCP(s,("reqQHT",))
	hublist = recvTCP(s)
	return hublist

def addhub(ip, aggregateQHT):
	a.neighbours[ip] = aggregateQHT
	return a.get_aggregateQHT()

def removehub(ip):
	a.remove_neigbour(ip)
	joinCluster()

def addleaf(ip):
	a.add_leaf(ip)

def addfile(ip, filename, size):
	if ip not in a.leaves:
		try:
			a.leaves[ip] = requestQHT(ip)
		except Exception as e:
			print e.message
	else:
		a.add_file(ip, filename, size)

def removefile(ip, filename):
	a.remove_file(ip, filename)

def updateQHT(ip, QHT):
	if ip in a.leaves:
		d = a.leaves
	elif ip in a.neighbours:
		d = a.neighbours
	a.update_QHT(ip, d, QHT)
	return true

def removeleaf(ip, leafip):
	a.remove_leaf(leafip)

# todo
# def search():

func_map = {"addhub":addhub,"removehub":removehub,"addleaf":addleaf,"addfile":addfile,"removeleaf":removeleaf,"removefile":removefile,"updateQHT":updateQHT}

def main():
	select_call(func_map, HUB_TCP_PORT, HUB_UDP_PORT)
	threading.Thread(target = heartbeat).start()
	joinCluster()

main()