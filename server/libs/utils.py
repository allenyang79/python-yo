#utils for test
import sys,os,re
import email
import json
import logging
import math
import smtplib
import time
import uuid
import base64

from string import maketrans
from flask import Flask
from flask import request
from flask.ext.login import current_user
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
		print self.lr_snippet
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
#	map static folder with yeoman
#	map static file to yeoman app folder or .tmp folder
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



###
# create extract by request
###
def extractRequest(rules):
	print "extractRequest"
	ret = {}
	for field, rule in rules.iteritems():
		conf = rule.get('inputConfig', {})
		if conf.get("mustReject", False):
			continue
		"""
		if conf.get("mustAccept", False):
			pass
		elif current_user.has_permission(conf.get("needPermission", [])):
			pass
		else:
			continue
		"""
		if field in request.values:
			t = conf.get('type', 'str')
			if t == "int":
				ret[field] = force_int(request.values[field])
			elif t == "float":
				ret[field] = force_float(request.values[field])
			elif t == "json":
				ret[field] = loadObject(field)
			elif t == 'boolean':
				if request.values.get(field) == 'true':
					ret[field] = True
				else:
					ret[field] = False
			else: # default to str
				ret[field] = request.values[field]
			if 'possibleValue' in conf:
				if ret[field] not in conf['possibleValue']:
					del ret[field]
		elif "default" in conf:
			if hasattr(conf["default"], '__call__'):
				ret[field] = conf["default"]()
			else:
				ret[field] = conf["default"]
	return ret



###
# get uuid
###
def getUUID():
	ret = base64.urlsafe_b64encode(uuid.uuid4().bytes)[:-2]
	if ret[0] == "-":
		ret = random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) + ret[1:]
	return ret
