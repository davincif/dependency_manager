import subprocess
import argparse

# Global Variables
REQUERIMENTS = 'requirements'
REQUERIMENTS_FILE = REQUERIMENTS + '.txt'


def intallpack(package_name: str):
	resp = subprocess.call(['pip', 'install', package_name])
	print('resp', resp)
	proc = subprocess.Popen(['pip', 'show', package_name], stdout=subprocess.PIPE)
	output = proc.stdout.read()
	print('resp', resp)
	print('output', output)


def main():
	parse = argparse.ArgumentParser(
		description='install pip packages and store then in a more clearn and organized way'
	)
	# parse.add_argument("install")


if __name__ == "__main__":
	print('working')
	intallpack('varenv')
	main()
