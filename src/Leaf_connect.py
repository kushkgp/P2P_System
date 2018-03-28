from collections import defaultdict
from utils import *
from node_utils import *
from env import *
import threading
import time
import json
import os
from Leaf import *

a = Leaf({})

def heartbeat():
	while True:
		print "sending heartbeat to Connected hubs"
		time.sleep(HUB_HEARTRATE)
		for hub in a.neighbours:
			addr = (hub,HUB_UDP_PORT)
			sendUDPpacket(addr, ("addleaf",))
			print "sent heartbeat to ", addr


def get_QHT(ip):
	return a.get_aggregateQHT()

def addFile(filename):
	size = a.addFile(filename)
	for hub in a.neighbours:
		addr = (hub,HUB_UDP_PORT)
		sendUDPpacket(addr, ("addfile",filename,size))
		print "sent add for a filename to ", addr

def removeFile(filename):
	a.removeFile(filename)
	for hub in a.neighbours:
		addr = (hub,HUB_UDP_PORT)
		sendUDPpacket(addr, ("addfile",filename))
		print "sent remove for a filename to ", addr

#to do func _map
func_map = {
	"reqQHT":get_QHT
}

def main():
	# WebCacheInfo = (WEB_CACHE_IP,WEB_CACHE_UDP_PORT,WEB_CACHE_TCP_PORT)
	threading.Thread(target = heartbeat).start()
	joinCluster(a, LEAF_CLUSTER_LIMIT, isLeaf=True)
	select_call(func_map, LEAF_TCP_PORT, LEAF_UDP_PORT)
	# Leaf(WebCacheInfo,1,PATH_VAR)

main()