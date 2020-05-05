import os
import json

from . import dmutils
from . import utils
from .dmexceptions import TreeNotInitilized, PackageNotOnTree


class DMTree:
	__root = {}
	prefix = './'
	tree_file_name = "dmtree.json"
	req_file_name = 'requirements.txt'
	dev_req_file_name = 'dev_requirements.txt'


	# Magic Methods
	def __init__(self, prefix: str=None, req_file_name: str=None, dev_req_file_name: str=None):
		"""
		Inilialize tree class, but does not craete loas the file tree.

		:param prefix: where the tree shall be mounted, default './' (the current directory).
		:type prefix: str
		:param req_file_name: the pypi requirements file for production, default 'requirements.txt'.
		:type req_file_name: str
		:param dev_req_file_name: the pypi requirements file for development, default 'dev_requirements.txt'.
		:type dev_req_file_name: str
		"""
		# setting attributes
		if prefix is not None:
			self.prefix = prefix
		if req_file_name is not None:
			self.req_file_name = req_file_name
		if dev_req_file_name is not None:
			self.dev_req_file_name = dev_req_file_name

		# craete tree file
		# self.tree_file_name = os.path.join(self.prefix, self.tree_file_name)
		# if not os.path.exists(self.tree_file_name):
		# 	with open(self.tree_file_name, 'w') as tree_file:
		# 		tree_file.write(json.dumps({}))

		# update requirements' file name
		self.req_file_name = os.path.join(self.prefix, self.req_file_name)
		self.dev_req_file_name = os.path.join(self.prefix, self.dev_req_file_name)


	# Public Methods
	def load(self) -> None:
		"""
		Load file tree.

		:raises: FileNotFoundError.
		"""
		# check existense and initialization
		if not os.path.exists(self.tree_file_name):
			raise FileNotFoundError("tree was never initialized and saved before.")
		with open(self.tree_file_name, 'r') as tree_file:
			self.__root = json.loads(tree_file.read())

	def save(self) -> dict:
		"""
		Save the tree structure to the file 'dmtree.json' at the directory specified in 'prefix'.

		:raises: TreeNotInitilized, FileNotFoundError, Exception.
		"""
		# check existense and initialization
		# if not os.path.exists(self.tree_file_name):
		# 	raise TreeNotInitilized("have you loaded of crated the tree? try 'load' or 'raise_tree' functions")

		# save
		try:
			with open(self.tree_file_name, 'w') as tree_file:
				tree_file.write(json.dumps(self.__root, indent='\t'))
		except FileNotFoundError as exp:
			raise FileNotFoundError(str(exp) + ". Try creatring the tree with 'raise_tree' fucntion first")
		except Exception as exp:
			raise Exception("unexpetec error: " + str(exp))

	def save_all(self):
		"""
		Save the tree file, and the dev and prod requirements files.

		:raises: TreeNotInitilized, FileNotFoundError, Exception.
		"""
		self.save()
		self.export(dev=True)
		self.export(dev=False)

	def raise_tree(self, save=True):
		self.__root = {
			'development': [],
			'production': [],
			'packs': {},
		}

		# puting all instaled pack in the tree
		pkglist = list(map(lambda x: x[0], dmutils.listpacks()))
		for pkg in pkglist:
			# treate in case the package is local
			pkg = pkg.split(' ')[0].strip()
			pkginfo = dmutils.getpackinfo(pkg)

			# add pack to tree
			self.__insertpack(pkginfo['name'], pkginfo['version'], pkginfo['requires'], pkginfo['required-by'], False)

			# check if package requires itself
			toremove = []
			for requires in self.__root['packs'][pkginfo['name']]['requires']:
				if requires == pkginfo['name']:
					toremove.append(requires)
			if toremove:
				utils.list_remove_list(self.__root['packs'][pkginfo['name']]['requires'], toremove)

		# add as production
		self.__root['production'] = pkglist

		# save tree
		if save:
			self.save()

	def export(self, dev: bool=False, reload_tree: bool=False):
		"""
		Export to a requirement file all the dev or prod (whichever is chosen) dependencies.
		This is important to maintain compatibility with project that does not used this dependency manager.
		So all dependencies can be installed by using only pip.
		PS.: this function will try to load the tree in case it's not loaded. And of course will fail is the
		it was never created and saved.

		:param dev: True export the development tree, False for the production.
		:type dev: bool
		:param reload_tree: force reload tree.
		:type reload_tree: bool

		:raises: FileNotFoundError, Exception
		"""
		# load tree if needed
		if reload_tree or not self.__root:
			self.load_tree()

		# choose right tree to add
		self.__sort_dep()
		tree2add = None
		if dev:
			tree2add = self.__root['development']
		else:
			tree2add = self.__root['production']

		# save requirements files
		dependencies = []
		for dep in tree2add:
			dependencies.append((dep, self.__root['packs'][dep]['version']))

		req_str = "\n".join(map(lambda t: "{}={}".format(t[0], t[1]), dependencies))

		if dev:
			with open(self.dev_req_file_name, 'w') as req_file:
				req_file.write(req_str)
		else:
			with open(self.req_file_name, 'w') as req_file:
				req_file.write(req_str)

	def install_tree(self, dev: bool=False):
		"""
		Install all dependencies of the chosen tree.

		:param dev: False to only install production dependencies. True to install development too.
		:type dev: bool
		"""
		# load tree is needed
		if not self.__root:
			self.load_tree()

		# install prod
		for dep in self.__root['production']:
			dmutils.intallpack("{}=={}".format(dep, self.__root['packs'][dep]['version']), nodeps=True)

		# install dev
		if dev:
			for dep in self.__root['development']:
				dmutils.intallpack("{}=={}".format(dep, self.__root['packs'][dep]['version']), nodeps=True)

	def install_pack(self, packname: str, version: str='', dev: bool=False):
		"""
		Install the requested pack and all its dependencies.

		If the no version is provided, the newer version will be installed.
		If the package and version request is already intalled, or the version
		is alraedy the newest and no version was provided, an exception will rise.
		If you with to change de dev or pord state of a pack, call 'move_dependency'.

		:param packname: The package name.
		:type packname: str
		:param version: The package version.
		:type version: str
		:param dev: Where to install the pack, True for dev, False for prod.
		:type dev: bool
		"""
		# check if dependency already exists
		if 'packname' in self.__root['packs']:
			# check if and specific versions is required
			if version:
				# check if the version already installed
				if version == self.__root['packs'][packname]['version']:
					raise Exception("package already installed")
			else:
				# check if there is newer versions
				version = self.__root['packs'][packname]['version']
				versions = dmutils.getversions(packname)
				if versions.index('1.0.0') < len(versions) - 1:
					# install newer version
					version = versions[-1]
				else:
					raise Exception("newest version already installed")

			# check if need to change dev to prod vice versa
			if (dev and not self.__root['packs'][packname]['dev']) or (not dev and self.__root['packs'][packname]['dev']):
				self.move_dependency(packname)

		# install pack
		dmutils.intallpack(packname, version)

		# get info
		packinfo = dmutils.getpackinfo(packname)
		self.__insertpack(packname, packinfo['version'], packinfo['requires'], packinfo['required-by'], dev)
		self.make_head(packname)

		# add dependencies
		if self.__root['packs'][packname]['requires']:
			self.__add_dependencies(packname, dev=dev)

		# update in dev or prod (whoever was choosen)

		# save
		self.__sort_dep()
		self.save_all()

	def uninstall(self, packname: str):
		"""
		Uninstall the package and all it's dependencies! Taking care to do not delete a
		package requested by another pack. This fucntion also moves packs from dev to prod
		in case it's needed after the uninstation.

		:param packname: The package name.
		:type packname: str
		"""
		# get remotion tree
		remotion_tree = self.get_dependency_list(packname)

		# check if no other packs needs any pack in the romotion tree
		# and remove it from the remotion tree
		pack_saved = {}
		for pack in self.__root['packs']:
			if pack not in remotion_tree:
				for dep in self.__root['packs'][pack]['requires']:
					if dep in remotion_tree:
						remotion_tree.remove(dep)

						# store update dev/prod status
						if dep in pack_saved:
							if pack_saved[dep] and not self.__root['packs'][pack]['dev']:
								pack_saved[dep] = False
						else:
							pack_saved[dep] = self.__root['packs'][pack]['dev']
			elif self.__root['packs'][pack]['head'] and pack != packname:
					remotion_tree.remove(pack)

		# update dev/prod status
		for pack in pack_saved:
			self.__root['packs'][pack]['dev'] = pack_saved[pack]

		# uninstall it
		for pack in remotion_tree:
			dmutils.unintallpack(pack)

		# remove all uninstalled packs from the __root
		for pack in remotion_tree:
			del self.__root['packs'][pack]

		# upate and save dependency list
		self.__sort_dep()
		self.save_all()

	def move_dependency(self, packname: str):
		"""
		Move the given dependency, if it is dev, move to prod, vice versa.
		OBS.: this function saves the tree and the requiments files in the end.

		:param packname: The package name.
		:type packname: str
		"""
		dev = None
		change_to = ''
		change_from = ''

		# check existency
		if packname not in self.__root['packs']:
			raise PackageNotOnTree("{} does not exists".format(packname))

		# choose change direction
		if self.__root['packs'][packname]['dev']:
			change_from = 'development'
			change_to = 'production'
			dev = False
		else:
			change_from = 'production'
			change_to = 'development'
			dev = True

		# check dev/prod consistency
		# if I'm going dev, no father should be prod.
		sontree = self.get_dependency_list(packname)
		sontree.remove(packname)
		if dev:
			fathertree = self.get_ascendency_list(packname)
			fathertree.remove(packname)
			for father in fathertree:
				# cant move requested pack
				if not self.__root['packs'][father]['dev']:
					raise Exception("Some other package in the production need this package!")


			# update dev/prod condition
			self.__root['packs'][packname]['dev'] = dev

			# check if any son needs to be updated
			for son in sontree:
				# do not update heads
				if self.__root['packs'][son]['head']:
					continue

				change = True
				for required in self.__root['packs'][son]['required-by']:
					if not self.__root['packs'][required]['dev']:
						change = False
						break
				if change:
					self.__root['packs'][son]['dev'] = True

		# If I'm going prod, no son should remains dev
		else:
			# move along all sons to prod too
			for son in sontree:
				self.__root['packs'][son]['dev'] = False

		# save
		self.__sort_dep()
		self.save_all()

	def get_dependency_list(self, packname: str) -> list:
		"""
		:returns: A list with all packages in which the given pack is dependent.
		:rtype: list
		"""
		deplist = [packname]
		for dep in self.__root['packs'][packname]['requires']:
			deplist += self.get_dependency_list(dep)

		return deplist

	def get_ascendency_list(self, packname: str) -> list:
		"""
		:returns: A list with all packages dependent on the given pack.
		:rtype: list
		"""
		deplist = [packname]
		for dep in self.__root['packs'][packname]['required-by']:
			deplist += self.get_ascendency_list(dep)

		return deplist

	def make_head(self, packname: str, unhead: bool=False) -> bool:
		"""
		Transforme the given package in a head package
		:returns: the previus head condition of the given package
		:rtype: bool
		"""
		prev = self.__root['packs'][packname]['head']
		self.__root['packs'][packname]['head'] = not unhead

		# save updated tree
		self.save()

		return prev

	def getinfo(self, packname: str, complete: bool=False) -> dict:
		"""
		get info about the requested pack.

		:param packname: The package name.
		:type packname: str
		:param complete: if Flase, returns only the main information, present in dmtree.json.
		If True, also get informatin from pip.
		:type complete: bool

		:returns: all information requested.
		:rtype: dict
		"""
		info = None

		if packname not in self.__root['packs']:
			info = {
				"NOT INSTALLED": "PACKAGE NOT INSTALLED"
			}
			info['available-versions'] = dmutils.getversions(packname)
		elif complete:
			info = dmutils.getpackinfo(packname)
			info['head'] = self.__root['packs'][packname]['head']
			info['dev'] = self.__root['packs'][packname]['dev']
			info['available-versions'] = dmutils.getversions(packname)
		else:
			info = self.__root['packs'][packname].copy()

		return info


	# Private Methods
	def __add_dependencies(self, pack: str, dev: bool=False):
		"""
		Recursively add to the tree all the dependence of given package.

		:param dev: Where to install the pack, True for dev, False for prod.
		:type dev: bool
		"""
		# add pack dependency
		for req in self.__root['packs'][pack]['requires']:
			# check if dependency already exists
			if req in self.__root['packs'][pack]:
				# treat dev/prod dependency
				if not self.__root['packs'][pack]['dev'] and self.__root['packs'][pack]['dev']:
					self.__root['packs'][pack]['dev'] = False
			else:
				# insert pack
				packinfo = dmutils.getpackinfo(req)
				self.__insertpack(req, packinfo['version'], packinfo['requires'], packinfo['required-by'], dev)

				# add depedencies of the dependency
				if self.__root['packs'][req]['requires']:
					self.__add_dependencies(req, dev=dev)

	def __insertpack(self, name: str, version: str, requires: list, required_by: list, dev: bool):
		"""
		Insert the given pack into the tree.

		:param name: The package name.
		:type name: str
		:param version: The package version.
		:type version: str
		:param requires: The names of required package by the installed package.
		:type requires: list
		:param required_by: The names of the package whos requires the installed package.
		:type required_by: list
		:param dev: if the package is a development or production package.
		:type dev: bool
		"""
		self.__root['packs'][name] = {
			'head': True if not required_by else False,
			'version': version,
			'requires': requires,
			'required-by': required_by,
			'dev': dev,
		}

	def __sort_dep(self):
		"""
		Walks through the tree separating dev and prod dependencies. You must call this funciton
		before exporting the tree.
		"""
		self.__root['development'].clear()
		self.__root['production'].clear()
		for dep in self.__root['packs']:
			if self.__root['packs'][dep]['dev']:
				self.__root['development'].append(dep)
			else:
				self.__root['production'].append(dep)


	# Getters and Setters
	@property
	def root(self):
		return self.__root.copy()

	@root.setter
	def root(self, setto):
		raise Exception("Do not set this property by yourself! Use the interface")
