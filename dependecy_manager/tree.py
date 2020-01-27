class Dmnode():
	name: str
	version: str
	sons = None
	father = None

	def __init__(self, name, version, father=None):
		self.name = name
		self.version = version
		self.father = father
		self.sons = []

	def __str__(self):
		return "%s==%s" % (self.name, self.version)

	def add_son(self, name, version):
		son = Dmnode(name, version, self)
		self.sons.append(son)

	def dictionarify(self, tree={}):
		tree[self.name] = {
			'version': self.version,
			'sons': {},
		}

		# add son's trees
		for son in self.sons:
			tree[self.name][sons][son.name] = son.dictionarify(self, tree[self.name].sons)
