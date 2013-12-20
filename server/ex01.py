import gevent
import time
from gevent import socket,Greenlet


urls=['www.google.com','tw.yahoo.cm','www.yam.com']
print urls

#spawn:
jobs=[gevent.spawn(socket.gethostbyname,url) for url in urls]
print jobs

gevent.joinall(jobs,timeout=2)
print [job.value for job in jobs]

for job in jobs:
	print job.value

fn=lambda v1,v2,v3:v1*v1+v2*v2+v3*v3
print fn(1,2,3)


def doTask(name,num):
	print "start task:%s" % name
	for i in range(num):
		#time.sleep(1)
		print "work %s" % name

jobs=[
		{'name':"aaa",'num':3},
		{'name':"bbb",'num':5},
		{'name':"ccc",'num':4}
	]

job={'name':'AAA','num':10}
g=Greenlet(doTask,job['name'],job['num'])
g.start()
print "next"

print "====run spawn===="
jobs=[gevent.spawn(doTask,job['name'],job['num']) for job in jobs]
gevent.wait(jobs)
print "job complete"
