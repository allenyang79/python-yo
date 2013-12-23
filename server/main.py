import os,sys
from flask import Flask,request,url_for,send_from_directory
from gevent.wsgi import WSGIServer
from werkzeug.serving import run_with_reloader
from werkzeug.debug import DebuggedApplication
from werkzeug.contrib.profiler import ProfilerMiddleware
from werkzeug.exceptions import NotFound
#from werkzeug.wrappers import Request,Response
#from utils import Foo,Bar,hello

libs_path = os.path.abspath('libs')
sys.path.append(libs_path)
import utils
import livereload_middleware

config={}
config['debug']=True
config['root_dir'] = os.path.dirname(os.path.abspath(__file__));
config['static_app_dir'] = config['root_dir']+'/../static/app'
config['static_dist_dir'] = config['root_dir']+'/../statc/dist'
config['static_tmp_dir'] = config['root_dir']+'/../static/.tmp'

#map static folder with yeoman
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
		print filepath
		if os.path.exists(filepath) and  os.path.isfile(filepath):
			return send_from_directory(config['static_app_dir'], filename,cache_timeout=cache_timeout)
		#scan .tmp file
		filepath="{}/{}".format(config['static_tmp_dir'],filename)
		if os.path.exists(filepath) and os.path.isfile(filepath):
			return send_from_directory(config['static_tmp_dir'], filename,cache_timeout=cache_timeout)
		raise NotFound()

	def make_response(self,rv):
		print "[MyFlask]make_response"
		return rv

	def process_response(self,response):
		response = super(MyFlask,self).process_response(response)
		return response



#end MyFlask
app=MyFlask(__name__)

#=end poit====
@app.route('/')
def hello_world():
	return 'this is index'


@app.route('/test_static')
def test_static():
	return url_for('static', filename='style.css')

#=server run===
if __name__ == '__main__':

	#app.debug=True
	#app.run()
	#package app by middleWare

	if config['debug']:
		#debugMode
		app=utils.LiveReloadMiddleware(app)
		wsgiApp= DebuggedApplication(app)
		@run_with_reloader
		def run_server():
			#http_server=WSGIServer(('',5000),Mid(simple_app))
			http_server=WSGIServer(('',5000),wsgiApp)
			http_server.serve_forever()
		run_server()
	else:
		#production
		http_server=WSGIServer(('',5000),app)
		http_server.serve_forever()

