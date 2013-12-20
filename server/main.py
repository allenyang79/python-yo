import os,sys
from flask import Flask,request,url_for,send_from_directory
from gevent.wsgi import WSGIServer
from werkzeug.serving import run_with_reloader
from werkzeug.debug import DebuggedApplication
from werkzeug.contrib.profiler import ProfilerMiddleware
from werkzeug.exceptions import NotFound
from werkzeug.wrappers import Request,Response
#from utils import Foo,Bar,hello
import utils




config={}
config['debug']=True
config['root_dir'] = os.path.dirname(os.path.abspath(__file__));
config['static_app_dir'] = config['root_dir']+'/../static/app'
config['static_dist_dir'] = config['root_dir']+'/../statc/dist'
config['static_tmp_dir'] = config['root_dir']+'/../static/.tmp'


class Mid(object):
	def __init__(self,app):
		print "__init__"
		self.app=app
	def __call__(self,environ,start_response):
		def custom_start_response(status,headers,exc_info=None):
			print "__call__"
			print exc_info
			response=start_response('200 OK',[('Content-Type','text/plain')])
			return response
		return self.app(environ,custom_start_response)
		"""
		def custom_start_response(status,headers,exc_info=None):
			req = Request(environ,shallow=True)
			print req
			#print exc_info
			#print headers
			#print environ
			#print "script_name?"+environ['SCRIPT_NAME']
			#print "query?"+environ['QUERY_STRING']
			#print "path_info?"+environ['PATH_INFO']
			#print "content_type?"+environ['CONTENT_TYPE']
			start_response(status,headers,exc_info)
			return "oops"
		return self.app(environ,custom_start_response)
		"""

def simple_app(environ,start_response):
	status = "200 OK"
	body = "hello world"
	headers = [
		("server","Super Server"),
		("Content-Length",str(len(body))),
		("Content-Type","text/plain")
	]
	start_response(status,headers)
	return [body]

#app = Flask(import_name=flask_config['import_name'],static_folder=flask_config['static_folder'],static_url_path=flask_config['static_url_path']);
#app=Flask(__name__)
#utils.hello()
#foo=utils.Foo("foo")


class MyFlask(Flask):
	#overwrite static file mapping for develop
	def send_static_file(self,filename):
		#scan below dictionary
		if not self.has_static_folder:
			return RuntimeError('No static folder for this object')
		cache_timeout = self.get_send_file_max_age(filename)

		#scan static file
		filepath="{}/{}".format(self.static_folder,filename)
		if os.path.exists(filepath) and os.path.isfile(filepath):
			return send_from_directory(self.static_folder, filename,cache_timeout=cache_timeout)
		#scan app file
		filepath="{}/{}".format(config['static_app_dir'],filename)
		if os.path.exists(filepath) and  os.path.isfile(filepath):
			return send_from_directory(config['static_app_dir'], filename,cache_timeout=cache_timeout)
		#scan .tmp file
		filepath="{}/{}".format(config['static_tmp_dir'],filename)
		if os.path.exists(filepath) and os.path.isfile(filepath):
			return send_from_directory(config['static_tmp_dir'], filename,cache_timeout=cache_timeout)
		raise NotFound()
	
#end MyFlask
app=MyFlask(__name__)

#=end poit====
@app.route('/')
def hello_world():
	return 'this is index'

@app.route('/version')
def get_version():
	return "test"

@app.route('/test_static')
def test_static():
	return url_for('static', filename='style.css')



#=server run===
if __name__ == '__main__':
	#app.debug=True
	#app.run()

	#package app by middleWare
	midApp=Mid(app)

	if config['debug']:
		#debugMode
		wsgiApp= DebuggedApplication(midApp)
		@run_with_reloader
		def run_server():
			#http_server=WSGIServer(('',5000),Mid(simple_app))
			http_server=WSGIServer(('',5000),wsgiApp)
			http_server.serve_forever()
		run_server()
	else:
		#production
		http_server=WSGIServer(('',5000),midApp)
		http_server.serve_forever()

