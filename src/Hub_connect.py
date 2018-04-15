from collections import defaultdict
from Hub import Hub
from utils import *
from node_utils import *
from env import *
import threading
from threading import Lock
import time
import json
import inspect
import sys
import copy


istemp = False
if len(sys.argv)>1 and sys.argv[0]=="yes":
	istemp = True
a = Hub(istemp)

mutex = Lock()

def lineno():
	print "requesting mutex at ", inspect.currentframe().f_back.f_lineno+1

def lineno1():
	print "releasing mutex at ", inspect.currentframe().f_back.f_lineno+1

def lineno2():
	print "mutex acquired at ", inspect.currentframe().f_back.f_lineno-1

def heartbeat():
	addr1 = (WEB_CACHE_IP_1,WEB_CACHE_UDP_PORT)
	addr2 = (WEB_CACHE_IP_2,WEB_CACHE_UDP_PORT)
	while True:
		print "sending heartbeat"
		lineno()
		mutex.acquire()
		lineno2()
		try:
			sendUDPpacket(addr1, ("add",(a.get_leafCount(), a.get_neighbourCount()),a.istemp))
			sendUDPpacket(addr2, ("add",(a.get_leafCount(), a.get_neighbourCount()),a.istemp))
		except Exception as e:
			print e.message
		finally:
			lineno1()
			mutex.release()
		time.sleep(HUB_HEARTRATE)

def requestQHT(ip):
	addr = (ip,LEAF_TCP_PORT)
	s = initTCPSocket(addr)
	sendTCP(s,("reqQHT",))
	hublist = recvTCP(s)
	return hublist

def addhub(ip, aggregateQHT):
	lineno()
	mutex.acquire()
	lineno2()
	a.neighbours[ip] = aggregateQHT
	b = copy.deepcopy(a.get_aggregateQHT())
	lineno1()
	mutex.release()
	return b

def removehub(ip):
	lineno()
	mutex.acquire()
	lineno2()
	a.remove_neigbour(ip)
	lineno1()
	mutex.release()

def addleaf(ip):
	lineno()
	mutex.acquire()
	lineno2()
	a.add_leaf(ip)
	lineno1()
	mutex.release()

def addfile(ip, filename, size):
	lineno()
	mutex.acquire()
	lineno2()
	b = copy.deepcopy(a)
	lineno1()
	mutex.release()
	if ip not in b.leaves:
		try:
			b.leaves[ip] = requestQHT(ip)
		except Exception as e:
			print e.message
	else:
		lineno()
		mutex.acquire()
		lineno2()
		a.add_file(ip, filename, size)
		lineno1()
		mutex.release()
	

def removefile(ip, filename):
	lineno()
	mutex.acquire()
	lineno2()
	a.remove_file(ip, filename)
	lineno1()
	mutex.release()

def updateQHT(ip, QHT, isLeaf):
	lineno()
	mutex.acquire()
	lineno2()
	b = copy.deepcopy(a);
	lineno1()
	mutex.release()
	if isLeaf:
		if ip not in b:
			addleaf(ip)
	else:
		if ip not in a.neighbours:
			addhub(ip,QHT)
	b = a.update_QHT(ip, QHT, isLeaf)
	return b
	

def removeleaf(ip, leafip):
	lineno()
	mutex.acquire()
	lineno2()
	a.remove_leaf(leafip)
	lineno1()
	mutex.release()

def informQHT(ip, fromhub):
	lineno()
	mutex.acquire()
	lineno2()
	b = copy.deepcopy(a);
	lineno1()
	mutex.release()
	try:
		connectHub(fromhub, b, False)
	except Exception as e:
		print e.message

def search(ip, port, filename):
	addr = (ip, port)
	isLeaf = False
	isFound = False
	target = None
	print "searh query obtained for ", filename, " from ", ip
	lineno()
	mutex.acquire()
	lineno2()
	b = copy.deepcopy(a);
	lineno1()
	mutex.release()
	for leaf in b.leaves:
		if leaf==ip:
			continue
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
	print (isFound,isLeaf,target)
	sendUDPpacket(addr, (isFound, isLeaf, target))

func_map = {"addhub":addhub,"removehub":removehub,
			"addleaf":addleaf,"addfile":addfile,"removeleaf":removeleaf,
			"removefile":removefile,"updateQHT":updateQHT, "informQHT":informQHT,
			"search":search
			}

def update_cluster():
	while True:
		try:
			lineno()
			mutex.acquire()
			lineno2()
			b = copy.deepcopy(a);
			lineno1()
			mutex.release();
			joinCluster(b, HUB_CLUSTER_LIMIT, isLeaf = False)
		except Exception as e:
			print e.message
		finally:
			time.sleep(HUB_CLUSTER_UPDATE_RATE)

def main():
	threading.Thread(target = heartbeat).start()
	threading.Thread(target = update_cluster).start()
	select_call(func_map, HUB_TCP_PORT, HUB_UDP_PORT)

main()