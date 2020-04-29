import os
import json

import dmutils
import utils


__tree = {}
tree_file_name = "dmtree.json"
inited = False
req_file_name = 'requirements.txt'
dev_req_file_name = 'dev_requirements.txt'


# Public Functions
def init():
	global __tree
	global tree_file_name
	global inited
	global req_file_name
	global dev_req_file_name

	# craete tree file
	tree_file_name = os.path.join('./', tree_file_name)
	if not os.path.exists(tree_file_name):
		with open(tree_file_name, 'w') as tree_file:
			tree_file.write(json.dumps({}))

	# update requirements' file name
	req_file_name = os.path.join('./', req_file_name)
	dev_req_file_name = os.path.join('./', dev_req_file_name)

	inited = True

def load_tree() -> dict:
	global __tree
	global tree_file_name
	global inited

	# check existense and initialization
	if not inited:
		raise(Exception("tree module note initialized before use"))
	elif not os.path.exists(tree_file_name):
		raise(Exception("tree module note initialized before use"))
	with open(tree_file_name, 'r') as tree_file:
		__tree = json.loads(tree_file.read())

	return __tree

def save_tree() -> dict:
	global __tree

	# check existense and initialization
	if not inited:
		raise(Exception("tree module note initialized before use"))
	elif not os.path.exists(tree_file_name):
		raise(Exception("tree module note initialized before use"))
	with open(tree_file_name, 'w') as tree_file:
		tree_file.write(json.dumps(__tree, indent='\t'))

	return __tree

def raise_tree(save=True):
	global __tree

	tree = {
		'development': {},
		'production': {},
		'packs': {},
	}

	# puting all instaled pack in the tree
	pkglist = list(map(lambda x: x[0], dmutils.listpacks()))
	for pkg in pkglist:
		pkginfo = dmutils.getpackinfo(pkg)

		# add pack to tree
		tree['packs'][pkginfo['name']] = {
			'version': pkginfo['version'],
			'requires': pkginfo['requires'],
			'required-by': pkginfo['required-by'],
		}

		# check if package requires itself
		toremove = []
		for requires in tree['packs'][pkginfo['name']]['requires']:
			if requires == pkginfo['name']:
				toremove.append(requires)
		if toremove:
			utils.list_remove_list(tree['packs'][pkginfo['name']]['requires'], toremove)

	# update global tree
	__tree = tree

	# creating dependecy tree
	add_dependencies(pkglist)

	# save tree
	if save:
		save_tree()

	return __tree

def add_dependencies(packlist: list, dev: bool=False):
	global __tree

	# choose right tree to add
	tree2add = None
	if dev:
		tree2add = __tree['development']
	else:
		tree2add = __tree['production']

	# insert dependencies
	packlist = packlist.copy()
	index = 0
	while index < len(packlist):
		pkg = packlist[index]

		# check if pack was already inserted in tree
		for requires in __tree['packs'][pkg]['requires']:
			if requires in tree2add:
				# remove from root, and add as a leaf
				tree2add[pkg] = __tree['packs'][pkg].copy()
				tree2add[pkg]['dependencies'] = {}
				tree2add[pkg]['dependencies'][requires] = tree2add[requires]
				del tree2add[requires]

		# add dependency
		tree2add[pkg] = __tree['packs'][pkg].copy()

		# add depedency tree
		if len(tree2add[pkg]['requires']) > 0:
			for_removal = __add_dependency_recursively(tree2add[pkg])

			# remove already added depedency from list
			utils.list_remove_list(packlist, for_removal)

		# updating index
		try:
			index = packlist.index(pkg)
		except Exception as exp:
			pass
		finally:
			# that shall never happen
			index += 1

def export_tree(dev: bool=False, reload_tree=False, save=True) -> list:
	global __tree
	global req_file_name
	global dev_req_file_name

	# load tree if needed
	if reload_tree or not __tree:
		load_tree()

	# choose right tree to add
	tree2add = None
	if dev:
		tree2add = __tree['development']
	else:
		tree2add = __tree['production']

	dependencies = []
	for pack in tree2add:
		dependencies.append((pack, tree2add[pack]['version']))
		dependencies += __export_tree(tree2add[pack])
	dependencies = utils.list_rm_repetition(dependencies)

	# save requirements files
	if save:
		req_str = "\n".join(map(lambda t: "{}={}".format(t[0], t[1]), dependencies))

		if dev:
			with open(dev_req_file_name, 'w') as req_file:
				req_file.write(req_str)
		else:
			with open(req_file_name, 'w') as req_file:
				req_file.write(req_str)

	return dependencies

def install_pack(packname: str, dev: bool=False):
	global __tree

	# install
	dmutils.intallpack(packname)

	# update pack tree
	pkinfo = dmutils.getpackinfo(packname)
	__tree['packs'][pkinfo['name']] = {
		'version': pkinfo['version'],
		'requires': pkinfo['requires'],
		'required-by': pkinfo['required-by'],
	}
	roots = []
	for req in pkinfo['requires']:
		reqinfo = dmutils.getpackinfo(req)
		# check if dependency is already present and a same version was added
		if req in __tree['packs']:
			roots.append(req)
			if __tree['packs'][req]['version'] == reqinfo['version']:
				continue

		# add dependency to pack tree
		__tree['packs'][req] = {
			'version': pkinfo['version'],
			'requires': pkinfo['requires'],
			'required-by': pkinfo['required-by'],
		}

	# add dependency
	add_dependencies([pkinfo['name']] + pkinfo['requires'], dev=dev)

	# choose right tree to add
	tree2add = None
	if dev:
		tree2add = __tree['development']
	else:
		tree2add = __tree['production']

	# re add as root
	for pack in roots:
		tree2add[pack] = __tree['packs'][pack]

	# save
	save_tree()
	export_tree(dev=dev, save=True)

def uninstall_pack(dev: bool=False, remove_tree: bool=True):
	pass

# Private Functions
def __remove_tree(pack_name: str):
	pass

def __export_tree(root: dict):
	dependencies = []

	# check if there are dependencies
	if 'dependencies' not in root:
		return dependencies

	# get in depth dependencies
	for dep in root['dependencies']:
		dependencies.append((dep, root['dependencies'][dep]['version']))
		dependencies += __export_tree(root['dependencies'][dep])

	return dependencies

def __add_dependency_recursively(tree: dict, rmpacks: list=[]):
	global __tree

	# update packs to be removed
	rmpacks = utils.list_rm_repetition(rmpacks + tree['requires'])

	# add inner dependencies
	for pkg in tree['requires']:
		if pkg in __tree['packs']:
			if 'dependencies' not in tree:
				tree['dependencies'] = {}
			elif pkg in tree['dependencies']:
				continue

			tree['dependencies'][pkg] = __tree['packs'][pkg].copy()
			if len(tree['dependencies'][pkg]['requires']) > 0:
				toremove = __add_dependency_recursively(tree['dependencies'][pkg], rmpacks)
				toremove = utils.list_rm_repetition(toremove + toremove)

	return rmpacks


# self init
init()
