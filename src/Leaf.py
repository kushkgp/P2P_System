import os
from collections import defaultdict

class Leaf:
	def __init__(self, FileList):
		self.neighbours = defaultdict()
		self.QHT = FileList
		self.hublist = defaultdict(lambda:(0,0))
		# self.WebCacheInfo = WebCacheInfo
		# self.HUBSCNT = nHubs
		# self.PATH = Path

	def addFile(self,filename):
		size = os.path.getsize(PATH + filename)
		self.FileList[filename] = size

	def removeFile(self,fileInfo,ip,port):
		size = os.path.getsize(PATH + filename)
		self.FileList.pop(filename)

	def addHub(self, ip):
		self.neighbours[ip]

	def removeHub(self, ip):
		if ip in self.neighbours:
			self.neighbours.pop(ip)
	def get_aggregateQHT(self):
		return self.QHT
	# to do update folder(collection of files in QHT)
	# addFolder