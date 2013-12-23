from flask.ext import pymongo
from pymongo import MongoClient
			
			


###########
#   ProjectModel
##########
class ProjectModel(object):
	def __init__(self):
		pass
	def create(self,obj):
		pass
	def save(self,obj):
		if obj['_id']:
			pass
		else:
			return None
			
	def bar(self):
		print "bar"


