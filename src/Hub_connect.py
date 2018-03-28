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

a = Hub()

mutex = Lock()

def lineno():
	print "requesting mutex at ", inspect.currentframe().f_back.f_lineno+1

def lineno1():
	print "releasing mutex at ", inspect.currentframe().f_back.f_lineno+1

def lineno2():
	print "mutex acquired at ", inspect.currentframe().f_back.f_lineno-1

def heartbeat():
	addr = (WEB_CACHE_IP,WEB_CACHE_UDP_PORT)
	while True:
		print "sending heartbeat"
		lineno()
		mutex.acquire()
		lineno2()
		try:
			sendUDPpacket(addr, ("add",(a.get_leafCount(), a.get_neighbourCount()) ))
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
	a.neighbours[ip] = aggregateQHT
	b = a.get_aggregateQHT()
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
	if ip not in a.leaves:
		try:
			a.leaves[ip] = requestQHT(ip)
		except Exception as e:
			print e.message
	else:
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
	if isLeaf:
		if ip not in a.leaves:
			lineno1()
			mutex.release()
			addleaf(ip)
		else:
			lineno1()
			mutex.release()
	else:
		if ip not in a.neighbours:
			addhub(ip,QHT)
		lineno()
		mutex.release()
		lineno2()
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
	try:
		connectHub(fromhub, a, False)
	except Exception as e:
		print e.message
	finally:
		lineno1()
		mutex.release()

def search(ip, randport, filename):
	addr = (ip, randport)
	isLeaf = False
	isFound = False
	target = None
	print "searh query obtained for ", filename, " from ", ip
	lineno()
	mutex.acquire()
	lineno2()
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
	lineno1()
	mutex.release()
	print (isFound,isLeaf,target)
	sendUDPpacket(addr, (isFound, isLeaf, target))

# todo
# updateQht hub to hub
# def search():

func_map = {"addhub":addhub,"removehub":removehub,
			"addleaf":addleaf,"addfile":addfile,"removeleaf":removeleaf,
			"removefile":removefile,"updateQHT":updateQHT, "informQHT":informQHT,
			"search":search
			}

def update_cluster():
	while True:
		lineno()
		mutex.acquire()
		lineno2()
		try:
			joinCluster(a, HUB_CLUSTER_LIMIT, isLeaf = False)
		except Exception as e:
			print e.message
		finally:
			lineno1()
			mutex.release()
			time.sleep(HUB_CLUSTER_UPDATE_RATE)

def main():
	threading.Thread(target = heartbeat).start()
	threading.Thread(target = update_cluster).start()
	select_call(func_map, HUB_TCP_PORT, HUB_UDP_PORT)

main()