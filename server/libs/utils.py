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


class LiveReloadMiddleware(object):
	def __init__(self,app,path_regexp=r'\.(htm|html)$',lr_snippet='<!--LiveReload snippet-->'):
		self.app=app
		self.lr_snippet=lr_snippet
		self.path_regexp=path_regexp
	def __call__(self,environ,start_response):
		print "[LiveReloadMiddleware]__call__"
		print environ['PATH_INFO']
		path_info=environ['PATH_INFO']
		match = re.search(self.path_regexp, path_info)
		if not match:
			return self.app(environ,start_response)
	
		print "[LiveReloadMiddleware]==match=="
		start_response_args = []
		#fake response output
		def dummy_start_response(status, headers, exc_info=None):
			print "[MyMid]dummy_start_response"
			start_response_args.append(status)
			start_response_args.append(headers)
			start_response_args.append(exc_info)

		#parse result
		app_iter = self.app(environ,dummy_start_response)
		output=""
		for line in app_iter:
			#output.write(line)
			output+=line

		output=re.sub("(<\/body>)",self.lr_snippet+"\\1",output)
		#header and body
		headers=[]
		for name,value in start_response_args[1]:
			if name.lower() != 'content-length':
				headers.append((name.lower(),value))
		headers.append(('Content-Length',str(len(output))))
		start_response(start_response_args[0],headers,start_response_args[2])
		return [output]

