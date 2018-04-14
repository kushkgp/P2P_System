from collections import defaultdict

class Hub:
	def __init__(self, istemp):
		self.leaves = defaultdict(lambda : defaultdict(lambda:0))
		self.neighbours = defaultdict(lambda : defaultdict())
		self.hublist = defaultdict(lambda:(0,0))
		self.istemp = istemp

	def add_leaf(self, ip):
		self.leaves[ip] 

	def remove_leaf(self, ip):
		if ip in self.leaves:
			self.leaves.pop(ip) 

	def add_neighbour(self, ip):
		self.neighbours[ip]

	def remove_neighbour(self, ip):
		if ip in self.neighbours:
			self.neighbours.pop(ip) 

	def update_QHT(self, ip, filelist, isLeaf):
		if isLeaf:
			self.leaves[ip] = filelist
			return True
		else:
			self.neighbours[ip] = filelist
			return self.get_aggregateQHT()

	def add_file(self, ip, filename, size = 0):
		if ip in self.leaves:
			self.leaves[ip][filename] = size
		else:
			raise Exception('ip not found in dict')

	def remove_file(self, ip, filename):
		if ip in self.leaves:
			if filename in self.leaves[ip]:
				self.leaves[ip].pop(filename)
			else:
				raise Exception("filename doesn't exists in dict")
		else:
			raise Exception('ip not found in dict')

	def local_search(self, filename):
		ans = []
		for leaf in self.leaves:
			if filename in self.leaves[leaf]:
				ans.append((leaf,self.leaves[leaf[filename]]))
		return ans

	def cluster_search(self, filename):
		ans = []
		for nearby_hub in self.neighbours:
			if filename in self.neighbours[nearby_hub]:
				ans.append(nearby_hub)
		return ans

	def get_aggregateQHT(self):
		ans = defaultdict()
		for leaf in self.leaves:
			for filename in leaf:
				ans[filename] = None
		return ans

	def get_leafCount(self):
		return len(self.leaves)

	def get_neighbourCount(self):
		return len(self.neighbours)