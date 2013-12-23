import os,sys
from flask import Flask,request,url_for,send_from_directory
from gevent.wsgi import WSGIServer
from werkzeug.serving import run_with_reloader
from werkzeug.debug import DebuggedApplication
from werkzeug.contrib.profiler import ProfilerMiddleware
from werkzeug.exceptions import NotFound

libs_path = os.path.abspath('libs')
sys.path.append(libs_path)
from utils import Static_Assets_Flask,Livereload_Middleware,Static_Assets_Middleware

#procress config 
print sys.argv
if len(sys.argv)==1:
	config={}
	config['debug']=True
	config['root_dir'] = os.path.dirname(os.path.abspath(__file__));
	config['static_folder']="static"
	config['static_folder_mapping'] = [config['root_dir']+'/../static/app', config['root_dir']+'/../static/.tmp']
elif len(sys.argv)>1:
	sys.exit()
	pass

app=Static_Assets_Flask(__name__)
app.static_folder=config['static_folder']
app.static_folder_mapping=config['static_folder_mapping']

#end point 
@app.route('/')
def index():
	return 'this is index'

@app.route('/foo')
def foo():
	return 'this is foo'
@app.route('/bar')
def bar():
	return 'this is var'



#==run flask app===
if __name__ == '__main__':
	#flask run
	#app.debug=True
	#app.run()
	#package app by middleWare

	if config['debug']:
		#debugMode
		app=Livereload_Middleware(app)
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
