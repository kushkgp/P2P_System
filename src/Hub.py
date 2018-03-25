from collections import defaultdict

class Hub:
	def __init__(self):
		self.leaves = defaultdict(lambda : defaultdict(lambda:0))
		self.neighbours = defaultdict(lambda : defaultdict())
		
	def add_leaf(self, ip, port):
		self.leaves[(ip, port)] 

	def remove_leaf(self, ip, port):
		if (ip, port) in self.leaves:
			self.leaves.pop((ip, port)) 

	def add_neighbour(self, ip, port):
		self.neighbours[(ip, port)]

	def remove_neighbour(self, ip, port):
		if (ip, port) in self.neighbours:
			self.neighbours.pop((ip, port)) 

	def update_QHT(self, ip, port, d, filelist):
		if (ip, port) in d:
			d[(ip, port)] = filelist
		else:
			raise Exception('ip and port not found in dict')

	def add_file(self, ip, port, d, filename, size = None):
		if (ip, port) in d:
			d[(ip, port)][filename] = size
		else:
			raise Exception('ip and port not found in dict')

	def remove_file(self, ip, port, d, filename):
		if (ip, port) in d:
			if filename in d[(ip, port)]:
				d[(ip, port)].pop(filename)
			else:
				raise Exception("filename doesn't exists in dict")
		else:
			raise Exception('ip and port not found in dict')

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