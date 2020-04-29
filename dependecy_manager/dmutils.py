import subprocess
from typing import Dict


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
				info[key] = list(map(lambda x: x.strip(), value.lower().split(','))) if value else []
			elif key == 'required-by':
				info[key] = list(map(lambda x: x.strip(), value.lower().split(','))) if value else []
			else:
				info[key] = value

	return info

def listpacks() -> [str, str]:
	proc = subprocess.Popen(['pip', 'freeze'], stdout=subprocess.PIPE)
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
