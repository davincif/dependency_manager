import pprint
import sys
import argparse

from .tree import DMTree


def make_parser(toparser: str) -> argparse.Namespace:
	command = sys.argv[1]
	namepace = None

	if command == 'init':
		parser = argparse.ArgumentParser(
			description="""create DM environment tree from existente installed packages.
			 Or starts one from scratch."""
		)

		namepace = parser.parse_args(toparser[2:])
	elif command == 'i' or command == 'install':
		parser = argparse.ArgumentParser(
			description="""Install the project.
			If required package is provided, install only that package.
			In that case, if the requested package alraedy is on the project,
			updated it according to the requrested version.
			"""
		)
		parser.add_argument(
			'-n', '--name',
			type=str,
			dest='name',
			required=False,
			default='',
			nargs='?',
			help="pack name: --name=my_pack_name"
		)
		parser.add_argument(
			'-v', '--version',
			type=str,
			dest='version',
			required=False,
			default='',
			nargs='?',
			help="pack version: --name=1.0.1rc0"
		)
		parser.add_argument(
			'-d', '--dev',
			type=bool,
			dest='dev',
			required=False,
			default=False,
			nargs='?',
			help="for a dev package do: --dev=True"
		)

		namepace = parser.parse_args(toparser[2:])

		# arguments validation
		assert namepace.name or not namepace.version, "-v/--version flag neededs -n/--name flag."
	elif command == 'u' or command == 'uninstall':
		parser = argparse.ArgumentParser(
			description="""
			Uninstall required package and its dependency. Maintaining possible cross dependencies
			with other packages, moving them if necessary, and updating the tree.
			"""
		)
		parser.add_argument(
			'-n', '--name',
			type=str,
			dest='name',
			required=True,
			nargs='?',
			help="pack name: --name=my_pack_name"
		)

		namepace = parser.parse_args(toparser[2:])

		# arguments validation
		assert namepace.name, "-n/--name flag needed specification"
	elif command == 'f' or command == 'info':
		parser = argparse.ArgumentParser(description="Get info about the requested pack.")
		parser.add_argument(
			'-n', '--name',
			type=str,
			dest='name',
			required=True,
			nargs='?',
			help="pack name: --name=my_pack_name"
		)
		parser.add_argument(
			'-e', '--extra',
			type=bool,
			dest='extra',
			required=False,
			default=False,
			nargs='?',
			help="return me extra information about the package."
		)

		namepace = parser.parse_args(toparser[2:])

		# arguments validation
		assert namepace.name, "-n/--name flag needed specification"
	elif command == 'm' or command == 'move':
		parser = argparse.ArgumentParser(
			description='Move package between environments, production for developer and vice versa.'
		)
		parser.add_argument(
			'-n', '--name',
			type=str,
			dest='name',
			required=True,
			nargs='?',
			help="pack name: --name=my_pack_name"
		)

		namepace = parser.parse_args(toparser[2:])

		# arguments validation
		assert namepace.name, "-n/--name flag needed specification"
	elif command == 'mh' or command == 'makehead':
		parser = argparse.ArgumentParser(
			description="""Make the given package head.
			 That is, the project is now directly dependent on this package.""",
		)
		parser.add_argument(
			'-n', '--name',
			type=str,
			dest='name',
			required=True,
			nargs='?',
			help="pack name: --name=my_pack_name"
		)
		parser.add_argument(
			'-rm', '--remove',
			type=bool,
			dest='remove',
			required=False,
			default=False,
			nargs='?',
			help="Instead of making the package 'head', remove this status from it: \"unhead\"."
		)

		namepace = parser.parse_args(toparser[2:])

	return namepace

def main():
	# build command help
	parser = argparse.ArgumentParser(description='Manage Python Projects Dependency Tree.')
	parser.add_argument(
		'init',
		type=str,
		nargs='*',
		help='create DM environment tree from existente installed packages. Or starts one from scratch.',
	)
	parser.add_argument(
		'i - install',
		type=str,
		nargs='*',
		help='install the given packages',
	)
	parser.add_argument(
		'u - uninstall',
		type=str,
		nargs='*',
		help='uninstall the given packages.',
	)
	parser.add_argument(
		'f - info',
		type=str,
		nargs='?',
		help='Show info about the package.',
	)
	parser.add_argument(
		'm - move',
		type=str,
		nargs='*',
		help='Move package between environments, production for developer and vice versa.',
	)
	parser.add_argument(
		'ex - export',
		type=str,
		nargs='*',
		help='export requirements files',
	)
	parser.add_argument(
		'mh - makehead',
		type=str,
		nargs='*',
		help="""Make the given package head.
		 That is, the project is now directly dependent on this package.""",
	)
	if len(sys.argv) < 2:
		parser.print_help()
		exit()

	# select and parse command
	command = sys.argv[1]
	args = make_parser(sys.argv)
	if args is None:
		args = parser.parse_args()

	# crate tree
	dmtree = DMTree()

	# execute command
	if command == 'init':
		dmtree.raise_tree()
		exit()
	else:
		dmtree.load()

	if command == 'i' or command == 'install':
		if not args.name:
			dmtree.install_tree(dev=args.dev)
		else:
			# install
			if args.version:
				dmtree.install_pack(args.name, args.version, args.dev)
			else:
				dmtree.install_pack(args.name, dev=args.dev)

			# save changes
			dmtree.export(dev=args.dev)
	elif command == 'u' or command == 'uninstall':
		dmtree.uninstall(args.name)
	elif command == 'f' or command == 'info':
		pp = pprint.PrettyPrinter(compact=True, indent=2)
		info = dmtree.getinfo(args.name, args.extra)
		pp.pprint(info)
	elif command == 'm' or command == 'move':
		dmtree.move_dependency(args.name)
	elif command == 'ex' or command == 'export':
		dmtree.export(dev=True)
		dmtree.export(dev=False)
	elif command == 'mh' or command == 'makehead':
			dmtree.make_head(args.name, unhead=args.remove)
	else:
		raise Exception("No command given or not recognized")


if __name__ == "__main__":
	main()
