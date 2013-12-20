class foo:
	#return instance
	def __init__(self,a,b,c):
		print a+b+c
		pass
	#apply function
	def __call__(self,a,b,c):
		print a*a+b*b+c*c
		pass

x=foo(1,2,3)
foo(1,2,3)
x(2,3,4)
