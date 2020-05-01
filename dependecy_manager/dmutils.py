import subprocess
from typing import Dict


def intallpack(package_name: str, version: str='', nodeps:bool=False) -> None:
	# construct package name with version if needed
	installstr = package_name if not version else "{}=={}".format(package_name, version)

	# construct command and flags
	command = ['pip', 'install']
	if nodeps:
		command.append(['--no-deps'])
	command.append(installstr)

	# execute command
	resp = subprocess.call(command)

def unintallpack(package_name: str) -> None:
	resp = subprocess.call(['pip', 'uninstall', package_name])

def getpackinfo(package_name: str) -> Dict[str, str]:
	# execute command
	proc = subprocess.Popen(['pip', 'show', package_name], stdout=subprocess.PIPE)
	proc.wait()

	# get and treate return
	lines = proc.stdout.read().decode('utf8')
	info = {}
	lines = list(map(lambda inf: inf.split(': '), lines.split('\n')))

	# process retun
	for line in lines:
		key = line[0].lower()
		if not not key and len(key) > 0:
			value = line[1]
			if key == 'name':
				info[key] = value.lower()
			elif key == 'requires':
				info[key] = list(map(lambda x: x.strip(), value.lower().split(','))) if value else []
			elif key == 'required-by':
				info[key] = list(map(lambda x: x.strip(), value.lower().split(','))) if value else []
			else:
				info[key] = value

	return info

def listpacks() -> [str, str]:
	# execute command
	proc = subprocess.Popen(['pip', 'freeze'], stdout=subprocess.PIPE)
	proc.wait()

	# process returned data
	lines = proc.stdout.read().decode('utf8')
	lines = list(filter(
		lambda inf: inf[0],
		map(
			lambda inf: list(map(
				lambda x: x.lower().strip(),
				inf.split('==')
				)),
			lines.split('\n')
		)
	))

	return lines

def getversions(package_name: str) -> list:
	# execute command
	proc = subprocess.Popen(['pip', 'install', package_name+'==CRASHME'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	proc.wait()

	# processed returned data
	lines = proc.stderr.read().decode('utf8')
	searchterm = "(from versions:"
	start = lines.find(searchterm) + len(searchterm)
	end = lines.find(")", start)
	lines = lines[start:end].split(',')
	lines = list(map(lambda x: x.strip(), lines))

	return 'lines'
