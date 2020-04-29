import os
import json
import pprint

import dmutils


tree_file_name = "dmtree.json"

# Public Functions
def init():
	global tree_file_name

	# craete tree file
	if not os.path.exists(os.path.join('./', tree_file_name)):
		with open(tree_file_name, 'w') as tree_file:
			tree_file.write(json.dumps({}))

	# make safe copy of requirements
	req_file_name = os.path.join('./', 'requirements.txt')
	if os.path.exists(req_file_name):
		os.rename(req_file_name, 'old_' + req_file_name)

def raise_tree():
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

	# creating dependecy tree
	add_dependencies(tree, pkglist)

	pp =pprint.PrettyPrinter(indent=2)
	pp.pprint(tree)
	print('\n')
	return tree

def add_dependencies(tree: dict, packlist: list, dev: bool=False):
	# choose right tree to add
	tree2add = None
	if dev:
		tree2add = tree['development']
	else:
		tree2add = tree['production']

	# insert dependencies
	index = 0
	while index < len(packlist):
		pkg = packlist[index]
		# add dependency
		tree2add[pkg] = tree['packs'][pkg].copy()

		# check root
		require_list = []
		for requires in tree2add[pkg]['requires']:
			if requires in tree2add:
				# remove from root, and add as a leaf
				tree2add[pkg]['dependencies'] = {}
				tree2add[pkg]['dependencies'][requires] = tree2add[requires]
				del tree2add[requires]
			else:
				require_list.append(requires)

		# add depedency tree
		if len(require_list) > 0:
			for_removal = __add_dependency_recursively(tree['packs'], tree2add[pkg])

			# remove already added depedency from list
			for rmpack in for_removal:
				try:
					packlist.remove(rmpack)
				except Exception as exp:
					pass

		try:
			index = packlist.index(pkg)
		except Exception as exp:
			pass
		finally:
			index += 1

def export_tree(dev: bool=False):
	pass

# Private Functions
def __add_dependency_recursively(packs: dict, tree: dict, rmpacks: list=[]):
	# update packs to be removed
	for req in tree['requires']:
		try:
			rmpacks.index(req)
		except Exception as exp:
			rmpacks.append(req)
		else:
			pass

	# to avoid messying up with tree's data
	packlist = tree['requires']

	# add inner dependencies
	for pkg in packlist:
		if 'dependencies' not in tree:
			tree['dependencies'] = {}

		if pkg in packs:
			tree['dependencies'][pkg] = packs[pkg].copy()
			if len(tree['dependencies'][pkg]['requires']) > 0:
				toremove = __add_dependency_recursively(packs, tree['dependencies'][pkg], rmpacks)
				for req in toremove:
					try:
						rmpacks.index(req)
					except Exception as exp:
						rmpacks.append(req)
					else:
						pass

	return rmpacks
