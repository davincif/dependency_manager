def list_rm_repetition(from_list: list) -> list:
	"""
	Remove all repeated elements from list 'from_list'.
	"""
	return list(dict.fromkeys(from_list))

def list_remove_list(from_list: list, remove_this: list) -> None:
	"""
	From list 'from_list' remove all itens in list 'remove_this'.
	PS.: 'from_list' is going to be modified!
	"""
	for rmpack in remove_this:
		try:
			from_list.remove(rmpack)
		except Exception as exp:
			pass
