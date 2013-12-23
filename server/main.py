import os,sys
from flask import Flask,request,url_for,send_from_directory
from gevent.wsgi import WSGIServer
from werkzeug.serving import run_with_reloader
from werkzeug.debug import DebuggedApplication
from werkzeug.contrib.profiler import ProfilerMiddleware
from werkzeug.exceptions import NotFound
from flask.ext import pymongo
from pymongo import MongoClient

sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/libs')
from utils import Static_Assets_Flask,Livereload_Middleware,Static_Assets_Middleware
from models import ProjectModel

#########################
#   procress config 
#########################
print sys.argv
if len(sys.argv)==1:
	config={}
	config['debug']=True
	config['root_dir'] = os.path.dirname(os.path.abspath(__file__));
	config['static_folder']="static"
	config['static_folder_mapping'] = [config['root_dir']+'/../static/app', config['root_dir']+'/../static/.tmp']

	config['db_host']='localhost'
	config['db_port']=27017
	config['db_name']='RichmediaDevToolKit'
	#config['db_user']=''
	#config['db_password']=''
elif len(sys.argv)>1:
	sys.exit()
	pass

#########################
#   DB
#########################
def get_db():
	db_client=MongoClient(config['db_host'],config['db_port'])
	db=db_client[config['db_name']]

	if 'db_user' in config and 'db_password' in config:
		db.authenticate(config['db_user'],config['db_password'])
	return db



########################
#   Flask App
########################
app=Static_Assets_Flask(__name__)
app.static_folder=config['static_folder']
app.static_folder_mapping=config['static_folder_mapping']

#########################
#   end point setting
#########################
@app.route('/')
def index():
	return 'this is index'

@app.route('/project/list')
def project_list():
	return 'this is project list'

@app.route('/project/edit',methods=['POST'])
def project_edit():
	return 'this is project edit'

@app.route('/project/test',methods=['GET','POST'])
def project_test():
	p=ProjectModel()
	p.foo()
	p.bar()
	return 'this is project edit'


##########################
# run flask app
##########################
if __name__ == '__main__':
	#flask run
	#app.debug=True
	#app.run()
	#package app by middleWare

	if config['debug']:
		#debugMode
		#middleWare
		app=Static_Assets_Middleware(app)
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
