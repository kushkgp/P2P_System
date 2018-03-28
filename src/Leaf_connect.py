from collections import defaultdict
from utils import *
from node_utils import *
from env import *
import threading
from threading import Lock
import time
import json
import os
from Leaf import *
from random import *
from cmd import Cmd
import os
import sys

dirpath = "./"
if len(sys.argv)>1:
	dirpath = sys.argv[1]
for (dirpath, dirnames, filenames) in os.walk(dirpath):
	filelist = filenames
	break

a = Leaf(filelist, dirpath)

fd = open("leaf_logs.txt","w")

mutex = Lock()

def heartbeat():
	while True:
		fd.write("\nsending heartbeat to Connected hubs")
		fd.flush()
		# print "Requesting mutex"
		mutex.acquire()
		# print "Acquired mutex"
		try:
			for hub in a.neighbours:
				addr = (hub,HUB_UDP_PORT)
				sendUDPpacket(addr, ("addleaf",))
				fd.write("\nsent heartbeat to "+str(addr))
				fd.flush()
		except Exception as e:
			print e.message
		finally:
			# print "Releasing mutex"
			mutex.release()
			time.sleep(LEAF_HEARTRATE)

def get_QHT(ip):
	# print "Requesting mutex"
	mutex.acquire()
	# print "Acquired mutex"
	b = a.get_aggregateQHT()
	# print "Releasing mutex"
	mutex.release()
	return b

def addFile(filename):
	# print "Requesting mutex"
	mutex.acquire()
	# print "Acquired mutex"
	try:
		size = a.addFile(filename)
		for hub in a.neighbours:
			addr = (hub,HUB_UDP_PORT)
			sendUDPpacket(addr, ("addfile",filename,size))
			fd.write("\nsent add for a filename to "+str(addr))
			fd.flush()
	except Exception as e:
		print e.message
	finally:
		# print "Releasing mutex"
		mutex.release()

def removeFile(filename):
	# print "Requesting mutex"
	mutex.acquire()
	# print "Acquired mutex"
	try:
		a.removeFile(filename)
		for hub in a.neighbours:
			addr = (hub,HUB_UDP_PORT)
			sendUDPpacket(addr, ("addfile",filename))
			fd.write("\nsent remove for a filename to "+str(addr))
			fd.flush()
	except Exception as e:
		print e.message
	finally:
		# print "Releasing mutex"
		mutex.release()

def download(leafip, hubip, filname):
	try:
		print "found on leaf: ", leafip
		print "starting download..."
		return True
	except Exception as e:
		fd.write(e.message)
		fd.flush()
		addr = (hubip, HUB_UDP_PORT)
		sendUDPpacket(addr, ("removeleaf", leafip))
		return False

# response = [isfound, isLeaf, ip]
def search_on_hub(currenthub, filename, fromhub = None):
	print "searching on hub: ", currenthub
	while True:
		randport = randint(CLIENT_UDP_MIN,CLIENT_UDP_MAX)
		s = initUDPrecvSocket(randport)
		for retrycount in range(SEARCH_RETRY_LIMIT):
			addr = (currenthub,HUB_UDP_PORT)
			print "Searching for ", filename, " from ", currenthub
			sendUDPpacket(addr, ("search",randport,filename))
			response,_ = recvUDPpacket(s, SEARCH_TIMEOUT_LIMIT)
			if response != "":
				break
		s.close()
		print response
		if response == "":							# if not responded
			addr = (WEB_CACHE_IP,WEB_CACHE_UDP_PORT)
			sendUDPpacket(addr, ("rem", currenthub))
			if fromhub!=None:
				addr = (fromhub, HUB_UDP_PORT)
				sendUDPpacket(addr, ("removehub", currenthub))
			return False
		elif response[0]:
			if response[1]:
				download_status = download(response[2], currenthub, filename)
				if download_status:
					return True
			else:									# hub redirection
				if fromhub==None:						# valid redirection (level 1)
					download_status = search_on_hub(response[2], filename, currenthub)
					if download_status:
						return True
				else:									# invalid redirection
					addr = (currenthub, HUB_UDP_PORT)
					sendUDPpacket(addr, ("informQHT", fromhub))
					return False
		else:										# not found
			return False

def search_and_download(filename):
	# print "Requesting mutex"
	mutex.acquire()
	# print "Acquired mutex"
	try:
		for hub in a.hublist:
			download_status = search_on_hub(hub, filename)
			if download_status:
				return True
	except Exception as e:
		print e.message
	finally:
		# print "Releasing mutex"
		mutex.release()
	return False

def getFile(filename):
	print "started searching..."
	download_status = search_and_download(filename)
	if download_status:
		return True
	b = get_hublist()							# retry with new latest hubs
	# print "Requesting mutex"
	mutex.acquire()
	# print "Acquired mutex"
	a.hublist = b
	# print "Releasing mutex"
	mutex.release()
	return search_and_download(filename)

class MyPrompt(Cmd):
	def do_download(self, args):
		"""downloads a file from p2p network, requires only one argument"""
		args = args.split()
		print args
		if len(args)!=1:
			print "use help to see usage"
			return
		download_status = getFile(args[0])
		if download_status:
			print "File successfully downloaded from the network"
		else:
			print "Eror in downloading"

	def do_quit(self, args):
		"""Quits the program."""
		print "Quitting from network"
		raise SystemExit

def update_cluster():
	while True:
		# print "Requesting mutex"
		mutex.acquire()
		# print "Acquired mutex"
		try:
			joinCluster(a, LEAF_CLUSTER_LIMIT, isLeaf=True)	
		except Exception as e:
			print e.message
		finally:
			# print "Releasing mutex"
			mutex.release()
			time.sleep(LEAF_CLUSTER_UPDATE_RATE)

#to do func _map
func_map = {
	"reqQHT":get_QHT
}

def main():
	# WebCacheInfo = (WEB_CACHE_IP,WEB_CACHE_UDP_PORT,WEB_CACHE_TCP_PORT)
	threading.Thread(target = heartbeat).start()
	threading.Thread(target = update_cluster).start()
	prompt = MyPrompt()
	prompt.prompt = '> '
	threading.Thread(target = prompt.cmdloop('Starting Client prompt...')).start()
	select_call(func_map, LEAF_TCP_PORT, LEAF_UDP_PORT)

main()