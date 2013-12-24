import os,sys
import json
import uuid
import copy
import time
from flask import Flask,request,url_for,send_from_directory
from gevent.wsgi import WSGIServer
from werkzeug.serving import run_with_reloader
from werkzeug.debug import DebuggedApplication
from werkzeug.contrib.profiler import ProfilerMiddleware
from werkzeug.exceptions import NotFound
#from flask.ext import pymongo
from pymongo import MongoClient

sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/libs')
from utils import Static_Assets_Flask,Livereload_Middleware,Static_Assets_Middleware,getUUID,extractRequest




#########################
#   procress config 
#########################
print sys.argv
if len(sys.argv)==1:
	config={}
	config['debug']=True
	config['host']='localhost'
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

########################
#   DB
#########################
def get_db():
	db_client=MongoClient(config['db_host'],config['db_port'])
	db=db_client[config['db_name']]
	if 'db_user' in config and 'db_password' in config:
		db.authenticate(config['db_user'],config['db_password'])
	return db
global db
db=get_db()

project_id=getUUID()
db.projects.save({'_id':project_id})
print "new project id:"
print project_id
