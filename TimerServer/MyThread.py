import threading
from time import ctime, sleep

class MyThread(threading.Thread):
	def __init__(self, func, args, name):
		super(myThread, self).__init__()
		self.name = name
		self.args = args
		self.func = func
		self.result = ""
	def run(self):
		print "start", self.name, "at :", ctime()
		self.result = apply(self.func, self.args)
		print "end", self.name, "at :", ctime()
	def getResult(self):
		return self.result