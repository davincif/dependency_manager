import subprocess
import argparse
from os import path
import json
import datetime
from typing import Dict

from tree import Dmnode


# Global Variables
REQUERIMENTS_FILE = 'requirements.txt'
BASE_PATH = '.'
BASE_DEPENDECIES_PATH = BASE_PATH
DMTREE = 'dmtree.json'


def main():
	global REQUERIMENTS_FILE
	global BASE_PATH
	global BASE_DEPENDECIES_PATH

	command_list = ["INSTALL", "MAKETREE"]
	install_flags = [
		('--dev', 'install as development dependecy'),
		('--prod', 'install as prodution dependency'),
	]

	parse = argparse.ArgumentParser(
		description='install pip packages and store then in a more clearn and organized way',
	)
	parse.add_argument(
		"command",
		type=str,
		choices=list(map(lambda x: x.lower(), command_list)),
		default="install",
		help="the command to be executed (case INsensitive)",
	)

	install_group = parse.add_argument_group('install')
	for flag in install_flags:
		install_group.add_argument(
			flag[0],
			type=bool,
			const=True,
			default=True if flag[0] == '--dev' else False,
			nargs='?',
			help=flag[1],
		)
	install_group.add_argument(
		'-bp --basepath',
		type=str,
		default=BASE_PATH,
		help='path to the project root',
	)
	install_group.add_argument(
		'-rf --requiredfile',
		type=str,
		default=REQUERIMENTS_FILE,
		help='name of the requirements',
	)
	install_group.add_argument(
		'-bdp --basedependencypath',
		type=str,
		default=BASE_DEPENDECIES_PATH,
		help='path from were the project dependency shall be loaded and saved (recomended to base the same as the project base_path)',
	)

	args = parse.parse_args()
	command_list = list(map(lambda x: x.upper(), command_list))

	# checking args
	command = args.command.upper()
	if command not in command_list:
		raise NameError("command '%s' not identified. Attention to lower case." % command)

	if command == 'INSTALL':
		if not (args.dev or args.prod):
			# this case shall never run
			raise Exception('--dev or --prod flag must be given to install command')

		install(args)
	elif command == 'MAKETREE':
		maketree()
	else:
		# this case shall never run
		raise NameError("Command '%s' not recognized." % command)

def install(args):
	print('INSTALL! \o/')
	is_dmtree(args)

def maketree():
	print('Command MAKETREE is still not implemented, sorry')

def is_dmtree(args, create=True):
	""" Checks if the given project is already managed by depecency_manager
	"""
	global BASE_PATH
	global BASE_DEPENDECIES_PATH
	global DMTREE

	if not path.isdir(BASE_PATH):
		raise NotADirectoryError("'%s' was not found or is not a directory" % BASE_PATH)
	elif not path.isdir(BASE_DEPENDECIES_PATH):
		raise NotADirectoryError("'%s' was not found or is not a directory" % BASE_DEPENDECIES_PATH)
	else:
		exists = path.isdir(DMTREE)
		if not exists and not create:
			raise FileNotFoundError("'%s' was not found or is not a file" % DMTREE)
		else:
			# loading dependency manager tree
			dmtree = {}
			if exists:
				with open(DMTREE, 'r') as ftree:
					dmtree = json.loads(ftree.readlines())

			# saving dependency manager tree
			with open(DMTREE, 'w') as ftree:
				ftree.write(json.dumps(dmtree))

def intallpack(package_name: str) -> None:
	resp = subprocess.call(['pip', 'install', package_name])

def getpackinfo(package_name: str) -> Dict[str, str]:
	proc = subprocess.Popen(['pip', 'show', package_name], stdout=subprocess.PIPE)
	lines = proc.stdout.read().decode('utf8')
	info = {}
	lines = list(map(lambda inf: inf.split(': '), lines.split('\n')))
	for line in lines:
		key = line[0].lower()
		if not not key and len(key) > 0:
			value = line[1]
			if key == 'name':
				info[key] = value.lower()
			elif key == 'requires':
				info[key] = value.lower().split(', ')
			else:
				info[key] = value

	return info

if __name__ == "__main__":
	main()
