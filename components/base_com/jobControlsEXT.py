'''
Matthew Ragan | matthewragan.com
'''
import socket
import json
# controls

ComClass = mod("comEXT").Com

class Job(ComClass):
	'''
		This is a bare bones Communcation class.

		This sample class has several important features that can be described here.


		Notes
		---------------
		Your notes about the class go here
 	'''

	def __init__(self, myOp):
		self.MyOp 			= myOp

		ComClass.__init__(self, myOp)
		
		print("Job Class init")
		pass
	
	def ApplyParVals(self, msg):
		op.Control.ApplyParVals( msg, self.MyOp.parent() )
		pass

	def ApplyPars(self, msg):
		op.Control.ApplyPars( msg )
		pass
