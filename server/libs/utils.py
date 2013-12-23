#utils for test
import sys,os,re
from flask import Flask,request,url_for,send_from_directory,current_app
from werkzeug.exceptions import NotFound

###
#  a wsgi middleware that can inject lrSnippet in html
###
class Livereload_Middleware(object):
	def __init__(self,app,path_regexp=r'\.(htm|html)$',lr_snippet='<!--LiveReload snippet-->'):
		self.app=app
		self.lr_snippet=lr_snippet
		self.path_regexp=path_regexp
	def __call__(self,environ,start_response):
		#print "[Livereload_Middleware]__call__"
		#print environ
		path_info=environ['PATH_INFO']
		match = re.search(self.path_regexp, path_info)
		if not match:
			return self.app(environ,start_response)
	
		#print "[Livereload_Middleware]==match=="
		start_response_args = []
		#fake response output
		def dummy_start_response(status, headers, exc_info=None):
			print "[Livereload_Middleware]dummy_start_response"
			start_response_args.append(status)
			start_response_args.append(headers)
			start_response_args.append(exc_info)

		#parse result
		app_iter = self.app(environ,dummy_start_response)
		if start_response_args[0][:3]!='200':
			return self.app(environ,start_response)

		output=""
		for line in app_iter:
			#output.write(line)
			output+=line
		if hasattr(app_iter, 'close'):
			app_iter.close()
		output=re.sub("(<\/body>)",self.lr_snippet+"\\1",output)

		#header and body
		headers=[]
		for name,value in start_response_args[1]:
			if name.lower() != 'content-length':
				headers.append((name.lower(),value))
		headers.append(('Content-Length',str(len(output))))
		#print "[Livereload_Middleware]"
		start_response(start_response_args[0],headers,start_response_args[2])
		return [output]


###
#  a wsgi middleware that will map static file to another folder
###
class Static_Assets_Middleware(object):
	def __init__(self,app):
		self.app=app
	def __call__(self,environ,start_response):
		print "[Static_Assets_Middleware]"
		print self.app
		print environ['PATH_INFO']
		print environ['SCRIPT_NAME']
		#detect 404 static file to remap

		return self.app(environ,start_response)
		
###
#   map static folder with yeoman
#   map static file to yeoman app folder or .tmp folder
###
class Static_Assets_Flask(Flask):
	#overwrite static file mapping for develop
	def send_static_file(self,filename):
		print "[Static_Assets_Flask]send_static_file"
		#return super(Static_Assets_Flask,self).send_static_file(filename)
		#scan below dictionary
		if not self.has_static_folder:
			return RuntimeError('No static folder for this object')
		cache_timeout = self.get_send_file_max_age(filename)
		folders=[]
		if isinstance(self.static_folder,basestring):
			folders.append(self.static_folder)
		if isinstance(self.static_folder_mapping,(list,tuple)):
			folders+=self.static_folder_mapping
		for folder in folders:
			filepath="{}/{}".format(folder,filename)
			if os.path.exists(filepath) and os.path.isfile(filepath):
				r=send_from_directory(folder, filename,cache_timeout=cache_timeout)
				return r
		raise NotFound()
