class TreeNotInitilized(Exception):
	def __init__(self, *args, **kwargs):
		"""
		PS.: Add a message to be printed out as positional argumento or name it 'msg='.
		"""
		msg = "Missing Tree Inilialization"
		if 'msg' in kwargs:
			args = ("{}: {}".format(msg, kwargs['msg']),)
		elif args:
			args = ("{}: {}".format(msg, args[0]),)
		else:
			args = (msg,)
		Exception.__init__(self, *args)

class PackageNotOnTree(Exception):
	def __init__(self, *args, **kwargs):
		"""
		PS.: Add a message to be printed out as positional argumento or name it 'msg='.
		"""
		msg = "Package not existent in dependency tree"
		if 'msg' in kwargs:
			args = ("{}: {}".format(msg, kwargs['msg']),)
		elif args:
			args = ("{}: {}".format(msg, args[0]),)
		else:
			args = (msg,)
		Exception.__init__(self, *args)
