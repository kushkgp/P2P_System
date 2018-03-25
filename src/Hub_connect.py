from collections import defaultdict
from Hub import Hub
from utils import *
import threading
import time
import pickle

# HUB_UDP_PORT = 
HUB_TCP_PORT = 21000
WEB_CACHE_IP = "192.168.0.6"
WEB_CACHE_PORT = 15000

a = Hub()

def heartbeat(addr):
	while True:
		print "sending heartbeat"
		time.sleep(1)
		sendUDPpacket(addr, ("add",(a.get_leafCount(), a.get_neighbourCount()) ))

def main():
	heartbeat_addr = (WEB_CACHE_IP,WEB_CACHE_PORT)
	threading.Thread(target = heartbeat,args = (heartbeat_addr,)).start()

main()


