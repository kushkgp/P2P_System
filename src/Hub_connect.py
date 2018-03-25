from collections import defaultdict
from Hub import Hub
from utils import *
import threading
import time
import json

# HUB_UDP_PORT = 
HUB_TCP_PORT = 21000
WEB_CACHE_IP = "192.168.0.6"
WEB_CACHE_UDP_PORT = 15000
WEB_CACHE_TCP_PORT = 50000


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
	s = socket.socket()
	s.bind(("",randint(10000,20000)))
	s.connect((WEB_CACHE_IP,WEB_CACHE_TCP_PORT))
	str = json.dumps(("req",))
	s.send(str.encode())
	ret = myreceive(s)
	s.close()
	return ret

def heartbeat():
	addr = (WEB_CACHE_IP,WEB_CACHE_UDP_PORT)
	while True:
		print "sending heartbeat"
		time.sleep(1)
		sendUDPpacket(addr, ("add",(a.get_leafCount(), a.get_neighbourCount()) ))

def join():
	a.hublist = get_hublist()


def main():
	threading.Thread(target = heartbeat).start()


main()
