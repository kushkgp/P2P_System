import os
from collections import defaultdict

class Leaf:
	def __init__(self, FileList, dirpath):
		self.dir = dirpath
		self.neighbours = defaultdict()
		self.QHT = defaultdict(lambda:0)
		for file in FileList:
			self.QHT[file] = os.path.getsize(self.dir + file)
		self.hublist = defaultdict(lambda:(0,0))
		self.temp_pid = 0
		
	def addFile(self, filename):
		size = os.path.getsize(self.dir + filename)
		self.QHT[filename] = size
		return size

	def removeFile(self, filename):
		size = os.path.getsize(self.dir + filename)
		self.QHT.pop(filename)

	def addHub(self, ip):
		self.neighbours[ip]

	def removeHub(self, ip):
		if ip in self.neighbours:
			self.neighbours.pop(ip)
	def get_aggregateQHT(self):
		return self.QHT

	# to do update folder(collection of files in QHT)
	# addFolder