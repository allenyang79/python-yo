#utils for test
import re







def hello():
	print "===HELLO==="

class Foo(object):
	def __init__(self,name):
		self.name=name
	def sayHi(self):
		print "hi.{}".format(self.name)

class Bar(Foo):
	def __init__(self):
		print "Bar extend from Foo"
		super(Bar, self).__init__("sub bar")
	def sayHi(self):
		super(Bar, self).sayHi()
		print "Oops"


