import json
from pprint import pprint

o=json.loads('{"a":"AAA","b":"BBB"}')
pprint(o)
print o['a']
print o['b']
#print p['a']
#print p['b']
o=[(0,{"aa":"AA","bb":"BB"}),(3,{"aa":"AAA"})]
print o

o="foo"
message="""
bar bar #{o}
"""
print message

