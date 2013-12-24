import os,sys
import json
import uuid
import copy
import time
import urllib2
import re
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
	config['mode']='dev'
	config['debug']=True
	config['host']='ec2-184-169-246-66.us-west-1.compute.amazonaws.com' #'184.169.246.66'
	config['port']=5000
	#config['host']='0.0.0.0'
	#config['port']=5000
	config['root_dir'] = os.path.dirname(os.path.abspath(__file__));
	config['static_folder']="static"
	config['static_folder_mapping'] = [config['root_dir']+'/../static/app', config['root_dir']+'/../static/.tmp']

	config['db_host']='localhost'
	config['db_port']=27017
	config['db_name']='RichmediaDevToolKit'
	#config['db_user']=''
	#config['db_password']=''
elif len(sys.argv)>1 and sys.argv[1]=='production':
	config={}
	config['mode']='production'
	config['debug']=False
	config['host']='localhost'
	config['port']=80
	config['root_dir'] = os.path.dirname(os.path.abspath(__file__));
	config['static_folder']=config['root_dir']+'/../static/dist'
	config['static_folder_mapping'] = [config['root_dir']+'/../static/app', config['root_dir']+'/../static/.tmp']

	config['db_host']='localhost'
	config['db_port']=27017
	config['db_name']='RichmediaDevToolKit'
else:
	print "unknow args"
	sys.exit()

#########################
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


########################
#   Flask App
########################
app=Static_Assets_Flask(__name__)
app.static_folder=config['static_folder']
app.static_folder_mapping=config['static_folder_mapping']
app.config['SERVER_HOST']=config['host']
app.config['SERVER_PORT']=config['port']

#########################
#   end point setting
#########################
@app.route('/')
def index():
	return 'appier richmedia toolkit'
####################
#   Project
####################
PROJECT_CONFIG = {
	'project_id':{
		'inputConfig':{'mustReject':True},
		'outputConfig':{'primary_key':True},
	},
	'public':{
		'inputConfig':{'type': 'boolean'}
	},
	'name':{},
	'template_type':{},
	'url':{},
	'assets_url':{},
	'click_through_url':{},
	'beacon1':{},
	'richmedia_info':{},
	'inject_snippet':{}
};

@app.route('/project/preview')
def project_preview():
	db=get_db()
	items=db.projects.find({'public':True}).sort('updated_at',-1)
	result=[]
	for item in items:
		item['creative_richmedia_id']=item['_id']
		result.append(item)
	return json.dumps({'code':200,'result':result})

@app.route('/project/preview/<project_id>')
def project_preview_one(project_id):
	result=db.projects.find_one({'_id':project_id})
	if result is None:
		return "proejct ad is parse fail";json.dumps({'code':0,'message':'project is not exist'})

	url=result['url']

	context=urllib2.urlopen(url).read()
	context=context.decode('utf-8')

	#prase body
	reg = '<body(?:.*?)>((?:\n|.)*)<\/body>'
	match=re.search(reg,context)
	context=match.group(1)

	#inject beacon1
	context=re.sub('(\${beacon1})',result['beacon1'],context)

	#injcet click_through_url
	context=re.sub('(\${CLICK_THROUGH_URL})',result['click_through_url'],context)

	#inject richmedia_info
	context=re.sub('(\${richmedia_info})',result['richmedia_info'],context)

	#replace __ASSETS__
	context=re.sub('(_ASSETS_)',result['assets_url'],context)

	#inject inject_snippet
	#context=re.sub('(<\/body>)',result['inject_snippet']+"\\1",context)
	if result['inject_snippet']:
		context+='<!--inject_snippet-->'+result['inject_snippet']

	from flask import make_response
	response = make_response(context)
	headers=response.headers
	headers.add('X-Adtype','mraid')
	if result['template_type']=='interstitial':
		headers.add('X-Orientation','*')
		headers.add('X-Fulladtype','interstitial')
	elif result['template_type']=='banner_320x50':
		headers.add('X-width',320)
		headers.add('X-height',50)
	elif result['template_type']=='300x250':
		headers.add('X-width',300)
		headers.add('X-height',250)

	headers.add('X-Clickthrough',result['click_through_url'])
	headers.add('X-Creativeid',result['_id'])
	headers.add('X-Imptracker','None')
	headers.add('X-Refreshtime',10000)
	headers.add('X-Failurl','None')
	headers.add('Content-Type','text/html; charset=utf-8')

	return response


@app.route('/project/read')
def project_raed():
	db=get_db()
	items=db.projects.find({'public':True}).sort('updated_at',-1)
	result=[]
	for item in items:
		result.append(item)
	return json.dumps({'code':200,'result':result})

@app.route('/project/read/<project_id>')
def project_read_one(project_id=None):
	db=get_db()
	result=db.projects.find_one({'_id':project_id})
	if result is None:
		return json.dumps({'code':0,'message':'project is not exist'})
	result['project_id']=result['_id']
	result.pop('_id',None)	
	return json.dumps({'code':200,'result':result})

@app.route('/project/edit',methods=['POST'])
def project_edit():
	db=get_db()
	if 'project_id' in request.values:
		existing = db.projects.find_one({'_id': request.values.get('project_id')})
		if existing is None:
			return {'code':0,'message':'project is not exist'}
		toSave=copy.deepcopy(existing)
	else:
		return {'code':0,'message':'project is not exist'}
		#toSave['_id']=getUUID()

	data=extractRequest(PROJECT_CONFIG)
	toSave.update(data)
	toSave['updated_at']=int(time.time())
	db.projects.save(toSave)
	return json.dumps(toSave)

@app.route('/project/test',methods=['GET','POST'])
def project_test():
	print "test"
	return 'this is project edit'


##########################
# run flask app
##########################
if __name__ == '__main__':
	#flask run
	#app.debug=True
	#app.host=config['host']
	#app.port=config['port']
	#app.run(host=config['host'],port=config['port'])
	#package app by middleWare

	if config['debug']:
		#debugMode
		#app.debug=True
		#app.run(host=config['host'],port=config['port'])
		#middleWare
		app=Static_Assets_Middleware(app)
		lr_snippet="""
    	<!-- livereload script -->
				<script src="http://{}:35729/livereload.js?snipver=1" type="text/javascript"></script>
     """.format(config['host'])
		app=Livereload_Middleware(app,lr_snippet=lr_snippet)
		wsgiApp= DebuggedApplication(app)
		@run_with_reloader
		def run_server():
			#http_server=WSGIServer(('',5000),Mid(simple_app))
			http_server=WSGIServer((config['host'],config['port']),wsgiApp)
			http_server.serve_forever()
		run_server()
	else:
		#production
		http_server=WSGIServer(('',config['port']),app)
		http_server.serve_forever()
