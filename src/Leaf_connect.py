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
import os,signal
import sys
import pyinotify
import inspect

import copy

dirpath = "./"
if len(sys.argv)>1:
	dirpath = sys.argv[1]
for (dirpath, dirnames, filenames) in os.walk(dirpath):
	filelist = filenames
	break

a = Leaf(filelist, dirpath)

fd = open("leaf_logs.txt","w")

mutex = Lock()


def lineno():
	print "requesting mutex at ", inspect.currentframe().f_back.f_lineno+1

def lineno1():
	print "releasing mutex at ", inspect.currentframe().f_back.f_lineno+1

def lineno2():
	print "mutex acquired at ", inspect.currentframe().f_back.f_lineno-1



def leaf_kill_handler(signum, frame):
	remove_temphub(WEB_CACHE_IP_1)
	print "leaf killed"
	exit()

signal.signal(signal.SIGINT, leaf_kill_handler)
signal.signal(signal.SIGTERM, leaf_kill_handler)

class EventHandler(pyinotify.ProcessEvent):
	def process_IN_CREATE(self, event):
		print "Creating:", event.pathname
		addFile(event.name)

	def process_IN_DELETE(self, event):
		print "Removing:", event.pathname
		removeFile(event.name)

def watch():
	wm = pyinotify.WatchManager()  # Watch Manager
	mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE  # watched events
	notifier = pyinotify.ThreadedNotifier(wm, EventHandler())
	notifier.start()
	wdd = wm.add_watch(a.dir, mask, rec=True)

def stop_watch():
	wm.rm_watch(wdd.values())
	notifier.stop()

def heartbeat():
	while True:
		fd.write("\nsending heartbeat to Connected hubs")
		fd.flush()
		# print "Requesting mutex"
		lineno()
		mutex.acquire()
		lineno2()
		b = copy.deepcopy(a.neighbours)
		lineno1()
		mutex.release()
		# print "Acquired mutex"
		try:
			for hub in b:
				addr = (hub,HUB_UDP_PORT)
				sendUDPpacket(addr, ("addleaf",))
				fd.write("\nsent heartbeat to "+str(addr))
				fd.flush()
		except Exception as e:
			print e.message
		finally:
			# print "Releasing mutex"
			time.sleep(LEAF_HEARTRATE)

def get_QHT(ip):
	# print "Requesting mutex"
	lineno()
	mutex.acquire()
	lineno2()
	# print "Acquired mutex"
	b = copy.deepcopy(a.get_aggregateQHT())
	# print "Releasing mutex"
	lineno1()
	mutex.release()
	return b

def addFile(filename):
	# print "Requesting mutex"
	lineno()
	mutex.acquire()
	lineno2()
	# print "Acquired mutex"
	size = a.addFile(filename)
	b = copy.deepcopy(a.neighbours)
	# print "Releasing mutex"
	lineno1()
	mutex.release()

	try:
		for hub in b:
			addr = (hub,HUB_UDP_PORT)
			sendUDPpacket(addr, ("addfile",filename,size))
			fd.write("\nsent add for a filename to "+str(addr))
			fd.flush()
	except Exception as e:
		print e.message

def removeFile(filename):
	# print "Requesting mutex"
	lineno()
	mutex.acquire()
	lineno2()
	a.removeFile(filename)
	b = copy.deepcopy(a.neighbours)
	# print "Releasing mutex"
	lineno1()
	mutex.release()

	# print "Acquired mutex"
	try:
		for hub in b:
			addr = (hub,HUB_UDP_PORT)
			sendUDPpacket(addr, ("removefile",filename))
			fd.write("\nsent remove for a filename to "+str(addr))
			fd.flush()
	except Exception as e:
		print e.message
		
def retrieve_file(ip, filename):
	lineno()
	mutex.acquire()
	lineno2()
	b = a.dir
	lineno1()
	mutex.release()
	return open(b+filename,"r").read()

# todo:  ftp protocol lib: pyftpdlib
def download(leafip, hubip, filename):
	try:
		print "found on leaf: ", leafip
		print "starting download..."
		addr = (leafip,LEAF_TCP_PORT)
		s = initTCPSocket(addr)
		sendTCP(s,("download",filename))
		print "Request for download sent"
		data = recvTCP(s)
		s.close()
		print "Data received"
		lineno()
		mutex.acquire()
		lineno2()
		b = a.dir
		lineno1()
		mutex.release()
		file = open(b+filename,"w+")
		file.write(data)
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
			addr = (WEB_CACHE_IP_1,WEB_CACHE_UDP_PORT)
			sendUDPpacket(addr, ("rem", currenthub))
			addr = (WEB_CACHE_IP_2,WEB_CACHE_UDP_PORT)
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
	lineno()
	mutex.acquire()
	lineno2()
	b = copy.deepcopy(a.hublist)
	lineno1()
	mutex.release()
	# print "Acquired mutex"
	try:
		for hub in b:
			download_status = search_on_hub(hub, filename)
			if download_status:
				return True
	except Exception as e:
		print e.message

	return False

def getFile(filename):
	print "started searching..."
	download_status = search_and_download(filename)
	if download_status:
		return True
	b = get_hublist(isLeaf = True)							# retry with new latest hubs
	# print "Requesting mutex"
	lineno()
	mutex.acquire()
	lineno2()
	# print "Acquired mutex"
	a.hublist = b
	# print "Releasing mutex"
	lineno1()
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
		stop_watch()
		raise SystemExit

def update_cluster():
	while True:
		try:
			joinCluster(a, mutex, LEAF_CLUSTER_LIMIT, isLeaf=True)	
		except Exception as e:
			print e.message
		finally:
			time.sleep(LEAF_CLUSTER_UPDATE_RATE)

def start_temphub(ip):
	lineno()
	mutex.acquire()
	lineno2()
	b = a.temp_pid
	lineno1()
	mutex.release()
	if b == 0 :
		cpid = os.fork()
		args = ["/usr/bin/xterm" , "-e" , "echo Temphub is started;" + "python ./Hub_connect.py yes" + ";echo Temphub is stopped;exec bash"]
		if cpid == 0:
			os.execv(args[0],args) 
		elif cpid>0:
			lineno()
			mutex.acquire()
			lineno2()
			a.temp_pid = cpid
			b = str(a.temp_pid)
			lineno1()
			mutex.release()

			print "temp hub is getting on with pid : " + b
		else:
			print "Cannot instantiate temphub"
	else :
		# check with waitpid
		print "temp hub on is already 'ON'" 

def remove_temphub(ip, my_ip=None):
	#todo sennd remove to Webcache
	if ip != WEB_CACHE_IP_1 and ip != WEB_CACHE_IP_2:
		return
	if my_ip is not None:
		try:
			addr = (WEB_CACHE_IP_1, WEB_CACHE_UDP_PORT)
			sendUDPpacket(addr, ("rem", my_ip))
			addr = (WEB_CACHE_IP_2, WEB_CACHE_UDP_PORT)
			sendUDPpacket(addr, ("rem", my_ip))
		except Exception as e:
			print e.message

	if a.temp_pid != 0:
		print "killing temp hub"
		os.kill(a.temp_pid,signal.SIGKILL)
		a.temp_pid = 0
	else :
		print "temp hub is not 'ON' yet"


func_map = {
	"reqQHT": get_QHT,
	"download": retrieve_file,
	"start_temphub": start_temphub,
	"remove_temphub": remove_temphub	
}

def main():
	# WebCacheInfo = (WEB_CACHE_IP,WEB_CACHE_UDP_PORT,WEB_CACHE_TCP_PORT)
	watch()
	threading.Thread(target = heartbeat).start()
	threading.Thread(target = update_cluster).start()
	prompt = MyPrompt()
	prompt.prompt = '> '
	threading.Thread(target = prompt.cmdloop, args = ("Starting Client prompt...",)).start()
	select_call(func_map, LEAF_TCP_PORT, LEAF_UDP_PORT)

main()