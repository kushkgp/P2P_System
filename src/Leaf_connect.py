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
			sendUDPpacket(addr, ("add",))
			print "sent heartbeat to ", addr



#to do func _map

def main():
	# WebCacheInfo = (WEB_CACHE_IP,WEB_CACHE_UDP_PORT,WEB_CACHE_TCP_PORT)
	threading.Thread(target = heartbeat).start()
	joinCluster(a, LEAF_CLUSTER_LIMIT, isLeaf=True)
	select_call(func_map, LEAF_TCP_PORT, LEAF_UDP_PORT)
	# Leaf(WebCacheInfo,1,PATH_VAR)

main()
# HubDownTokenWebCache = "rem"
# HubDownTokenHub = "removehub"
# SearchToken = "search"
# GetHubListToken = "req"
# ConnnectToHubToken = "updateQHT"
# AddFileToHubToken = "addfile"
# DeleteFileFromHubToken = "removefile"
# SendHeartBeatToHubToken = "addleaf"

# PATH_VAR = "/home/kv/Desktop"

# class Leaf:

# 	def __init__(self, WebCacheInfo , FileList = defaultdict(lambda : 0) , nHubs , Path):
# 		self.__WebCacheInfo = WebCacheInfo
# 		self.__FileList = FileList
# 		self.__HubAddressList = defaultdict(lambda : 0)
# 		self.__ConnectedHubs = defaultdict(lambda : 0)
# 		self.__HUBSCNT = nHubs
# 		self.__PATH = Path

# 	def GetHubList(self):
# 		s = initTCPSocket((self.__WebCacheInfo[0],self.__WebCacheInfo[2]))
# 		sendTCP(s,(GetHubListToken))
# 		return recvTCP(s)

# 	def ConnnectToHub(self,ip,port):
# 		s = initTCPSocket((ip,port))
# 		sendTCP(s,(ConnnectToHubToken,self.__FileList))
# 		return recvTCP(s)

# 	def AddFileToHub(self,fileInfo,ip,port):
# 		sendUDP((ip,port),(AddFileToHubToken,fileInfo))

# 	def DeleteFileFromHub(self,fileInfo,ip,port):
# 		sendUDP((ip,port),(DeleteFileFromHubToken,fileInfo))

# 	def Join(self):
# 		self.__HubAddressList = GetHubList()
# 		sorted(self.__HubAddressList.values())
# 		ConnectedHubsCnt = 0
# 		for key in self.__HubAddressList:
# 			if ConnnectToHub(key[0],key[1]) == True:
# 				ConnectedHubsCnt += 1
# 				self.__ConnectedHubs.append(key)
# 				if ConnectedHubsCnt == self.__HUBSCNT:
# 					break

# 	def AddFileName(self,filename):
# 		size = os.path.getsize(PATH + filename)
# 		self.__FileList[filename] = size
# 		for Hub in self.__ConnectedHubs:
# 			AddFileToHub((filename,size),Hub[0],Hub[1])

# 	def RemoveFileName(self,filename):
# 		size = os.path.getsize(PATH + filename)
# 		self.__FileList.pop(filename)
# 		for Hub in self.__ConnectedHubs:
# 			DeleteFileFromHub((filename,size),Hub[0],Hub[1])

# 	def SendHeartBeatToHub(self):
# 		sendUDP((ip,port),(SendHeartBeatToHubToken))

# 	def Search(self,filename):
# 		for Hub in self.__HubAddressList:
# 			retry_cnt = 0
# 			while retry_cnt < RETRY_LIMIT:
# 				s = initUDPrecvSocket(LEAF_UDP_PORT)
# 				recvUDPPacket(s,TIMEOUT_LIMIT)
# 				sendUDPPacket((Hub,HUB_UDP_PORT),(SearchToken,filename))
# 				msg,addr = recvUDPPacket(s,TIMEOUT_LIMIT)   # (ip_adres, 0/1:leaf/hub)
# 				if addr == None:
# 					retry_cnt+=1
# 				else:
# 					if msg[1] == 0:
# 						return msg[0]
# 					else:
# 						retry_cnt2 = 0
# 						while retry_cnt2 < RETRY_LIMIT:
# 							s = initUDPrecvSocket(LEAF_UDP_PORT)
# 							recvUDPPacket(s,TIMEOUT_LIMIT)
# 							sendUDPPacket((msg[0],HUB_UDP_PORT),(SearchToken,filename))
# 							msg,addr = recvUDPPacket(s,TIMEOUT_LIMIT)
# 							if addr == None:
# 								retry_cnt2+=1
# 							elif msg[1] == 0:
# 								return msg[0]
# 						sendUDPPacket((self.__WebCacheInfo[0],self.__WebCacheInfo[1]),(HubDownTokenWebCache,Hub))
# 						sendUDPPacket((Hub,HUB_UDP_PORT),(HubDownToken,msg[0]))
# 			sendUDPPacket((self.__WebCacheInfo[0],self.__WebCacheInfo[1]),(HubDownTokenWebCache,Hub))
# 		# select call - download file, request filelist
