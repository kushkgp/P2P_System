from collections import defaultdict
from Hub import Hub
from utils import *
from node_utils import *
from env import *
import threading
import time
import json

a = Hub()

def heartbeat():
	addr = (WEB_CACHE_IP,WEB_CACHE_UDP_PORT)
	while True:
		print "sending heartbeat"
		sendUDPpacket(addr, ("add",(a.get_leafCount(), a.get_neighbourCount()) ))
		time.sleep(HUB_HEARTRATE)

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

def updateQHT(ip, QHT, isLeaf):
	if isLeaf:
		if ip not in a.leaves:
			addleaf(ip)
	else:
		if ip not in a.neighbours:
			addhub(ip,QHT)
	return a.update_QHT(ip, QHT, isLeaf)
	

def removeleaf(ip, leafip):
	a.remove_leaf(leafip)


def informQHT(ip, fromhub):
	connectHub(fromhub, a, False)

def search(ip, randport, filename):
	addr = (ip, randport)
	isLeaf = False
	isFound = False
	for leaf in a.leaves:
		if filename in a.leaves[leaf]:
			isLeaf = True
			isFound = True
			target = leaf
			break
	if not isFound:
		for hub in a.neighbours:
			if filename in a.neighbours[hub]:
				isFound = True
				target = hub
				break
	sendUDPpacket(addr, (isFound, isLeaf, target))

# todo
# updateQht hub to hub
# def search():

func_map = {"addhub":addhub,"removehub":removehub,
			"addleaf":addleaf,"addfile":addfile,"removeleaf":removeleaf,
			"removefile":removefile,"updateQHT":updateQHT, "informQHT":informQHT,
			"search":search
			}

def main():
	threading.Thread(target = heartbeat).start()
	joinCluster(a, HUB_CLUSTER_LIMIT, isLeaf = False)
	select_call(func_map, HUB_TCP_PORT, HUB_UDP_PORT)

main()